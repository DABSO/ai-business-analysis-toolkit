import requests
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from langsmith import traceable
from typing import List, Union, Dict
import os
from PIL import Image
import io
import base64
import signal

from .browser_manager import BrowserManager

serper_api_key = os.getenv("SERPER_API_KEY")
scrapingant_api_key = os.getenv("SCRAPINGANT_API_KEY")

class ScrapingError(Exception):
    """Exception raised for errors during scraping."""
    def __init__(self, message="Scraping failed"):
        self.message = message
        super().__init__(self.message)

def scrape_url(url: str) -> dict:
    """
    Fetches the raw content of a URL using realistic browser headers and session.
    
    Args:
        url (str): The URL to scrape.
    
    Returns:
        dict: A dictionary containing the raw content of the response.
    """
    # Define realistic browser headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com/",
    }
    
    # Use a session to maintain cookies and connection
    session = requests.Session()
    session.chromium_path = os.getenv("CHROMIUM_PATH")
    session.headers.update(headers)
    
    try:
        # Fetch the URL
        response = session.get(url, timeout=10)
        print("received response with length", len(response.text))
        response.raise_for_status()  # Raise HTTPError for bad responses
        return {"raw_content": response.text}
    except requests.RequestException as e:
        return {"raw_content": f"Error fetching the URL: {e}"}

async def scrape_url_with_render(url: str) -> dict:
    """
    Fetches the raw content of a URL using pyppeteer with JavaScript rendering support.
    """
    print("scraping ", url[:100])
    
    try:
        # Add signal handling workaround for non-main threads
        signal.signal = lambda *args: None
        
        async with BrowserManager.get_page(url) as page:
            try:
                # Set timeout and other options
                
                page.setDefaultNavigationTimeout(30000)
                print("set timeout")

                # Navigate to the page
                response = await page.goto(url, {
                    'waitUntil': 'networkidle0',
                    'timeout': 30000
                })
                print(f"received response from {url} with status", response.status)
                
                if not response or not response.ok:
                    print(f"Failed to load page {url}: {response.status if response else 'No response'}")
                    raise ScrapingError(f"Failed to load page {url}: {response.status if response else 'No response'}")

                content = await page.content()
                print("received content with length", len(content))
               
                
                # Take one full screenshot into memory
                screenshot_bytes = await page.screenshot({
                    'fullPage': True,
                    'type': 'png'
                })
                
                # Open the screenshot with PIL
                img = Image.open(io.BytesIO(screenshot_bytes))
                width, height = img.size
                
                # Calculate number of segments needed
                segment_height = 1500
                num_segments = -(-height // segment_height)  # Ceiling division
                
                # Split into segments
                segments = []
                for i in range(num_segments):
                    start_y = i * segment_height
                    end_y = min(start_y + segment_height, height)
                    
                    # Crop the segment
                    segment = img.crop((0, start_y, width, end_y))
                    
                    # Resize the segment to reduce resolution
                    new_width = width // 3  # Reduce width by same factor as height (1500 -> 500)
                    new_height = segment_height // 3
                    segment = segment.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Convert segment to bytes
                    segment_bytes = io.BytesIO()
                    segment.save(segment_bytes, format='PNG')
                    segments.append(segment_bytes.getvalue())
                
                print(f"received {len(segments)} segments")
                # Convert segments to base64
                base64_segments = []
                for segment_bytes in segments:
                    # Convert bytes to base64
                    b64_data = base64.b64encode(segment_bytes).decode('utf-8')
                    base64_segments.append(f"data:image/png;base64,{b64_data}")
                
                
                
                print("received response with length", len(content))
                return {
                    "raw_content": content,
                    "screenshot_segments": base64_segments,
                }
            except ScrapingError as e:
                print(f"Scraping error during page operations for {url}: {e}")
                

                return {"raw_content": "Failed to scrape page"}

                
            except Exception as e:
                print(f"Error during page operations for {url}: {e}")
                return {"raw_content": f"Error processing the page: {str(e)}"}
                
    except Exception as e:
        print(f"Error scraping {url} with render: {str(e)}")
        return {"raw_content": f"Error fetching the URL: {str(e)}"}

def extract_text_from_html(html_content: str) -> str:
    """Extract readable text content from HTML using BeautifulSoup."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text and clean it up
        text = soup.get_text(separator='\n', strip=True)
        
        # Remove empty lines and excessive whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)
        
        return text
    except Exception as e:
        print(f"Error extracting text from HTML: {str(e)}")
        return None



@traceable
def serper_search(query):
    """Search the web using the Serper API."""
    # First get search results from Serper
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query
    })
    headers = {
        'x-api-key': serper_api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    search_results = json.loads(response.text)
    
    # Extract URLs to scrape
    urls_to_scrape = []
    if "organic" in search_results:
        urls_to_scrape.extend([item["link"] for item in search_results["organic"][:5]])
    
    # Scrape all URLs
    scraped_contents = [scrape_url(url) for url in urls_to_scrape]
    
    # Combine search results with scraped content
    tavily_formatted_result = {
        "results": []
    }
    
    for i, item in enumerate(search_results.get("organic", [])[:5]):
        scraped_content = scraped_contents[i]
        if scraped_content:
            tavily_formatted_result["results"].append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "content": item.get("snippet", ""),
                "raw_content": scraped_content.get("raw_content", "")
            })

    return tavily_formatted_result

async def scrape_all_urls(urls, use_render=False, batch_size=3):
    """Scrape URLs with controlled concurrency"""
    results = []
    
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        tasks = [scrape_url_with_render(url) for url in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        

    return results

@traceable
async def serper_search_async(search_queries, max_results=5, tavily_topic="general", tavily_days=30, include_images=True):
    """Performs asynchronous web searches using the Serper API."""
    try:
        # Store the current event loop for cleanup
        
        all_results = []
        use_render = True
        
        # Create a set to track scraped URLs
        scraped_urls = set()
        
        # Format queries for batch request
        queries_payload = [{"q": query} for query in search_queries]
        
        # Make single batch request to Serper
        url = "https://google.serper.dev/search"
        headers = {
            'x-api-key': serper_api_key,
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(queries_payload)) as response:
                all_search_results = await response.json()
        
        # Flatten the list of organic results
        organic_results = [
            item 
            for search_results in all_search_results 
            if "organic" in search_results
            for item in search_results["organic"][:max_results]
        ]
        
        unique_organic_urls = set([item["link"] for item in organic_results])
        print("scraping ", len(unique_organic_urls), " unique organic results")
        urls_to_scrape = list(unique_organic_urls)

        # Scrape only unique URLs
        scraped_contents = await scrape_all_urls(urls_to_scrape)
        
        # Create mapping of URL to scraped content for easy lookup
        url_to_content = {
            urls_to_scrape[i]: content 
            for i, content in enumerate(scraped_contents)
        }
        
        # Format results
        tavily_formatted_result = {
            "results": []
        }
        
        for item in organic_results[:max_results]:
            url = item.get("link", "")
            if url in url_to_content:
                scraped_content = url_to_content[url]
                tavily_formatted_result["results"].append({
                    "title": item.get("title", ""),
                    "url": url,
                    "content": item.get("snippet", ""),
                    "raw_content": scraped_content.get("raw_content", ""),
                    "screenshot_segments": scraped_content.get("screenshot_segments", []) if include_images else [],
                })
        
        all_results.append(tavily_formatted_result)
        
    
        return all_results
    except Exception as e:
        print(f"Error during serper_search_async: {e}")
        return []

def get_unique_urls(search_response):
    if isinstance(search_response, dict):
        sources_list = search_response.get('results', [])
    elif isinstance(search_response, list):
        sources_list = []
        for response in search_response:
            sources_list.extend(response.get('results', []) if isinstance(response, dict) else response)
    return sources_list

def deduplicate_and_format_sources(
    search_response: Union[Dict, List[Dict]],
    max_tokens_per_source: int,
    include_raw_content: bool = False,
    images_per_source: int = 5
) -> str:
    print("deduplicate_and_format_sources")
    """
    Takes either a single search response or list of responses and formats them.
    Limits the raw_content to approximately max_tokens_per_source.
    include_raw_content specifies whether to include the raw_content in the formatted string.
    
    Args:
        search_response: Either:
            - A dict with a 'results' key containing a list of search results
            - A list of dicts, each containing search results
            
    Returns:
        str: Formatted string with deduplicated sources
    """
    # Convert input to list of results
    if isinstance(search_response, dict):
        sources_list = search_response.get('results', [])
    elif isinstance(search_response, list):
        sources_list = []
        for response in search_response:
            sources_list.extend(response.get('results', []) if isinstance(response, dict) else response)
    else:
        raise ValueError("Input must be either a dict with 'results' or a list of search results")
    
    # Deduplicate by URL
    unique_sources = {}
    for source in sources_list:
        if source.get('url') and source['url'] not in unique_sources:
            unique_sources[source['url']] = source
    
    # Format output
    formatted_sources = [{
        "type": "text",
        "text": "Sources:\n\n"
    }]
    for source in unique_sources.values():
        formatted_text = ""
        formatted_text += f"Source {source.get('title', 'N/A')}:\n===\n"
        formatted_text += f"URL: {source.get('url', 'N/A')}\n===\n"
        formatted_text += f"Most relevant content from source: {source.get('content', 'N/A')}\n===\n"
        
        char_limit = max_tokens_per_source * 4
        text_content = extract_text_from_html(source.get('raw_content', ''))
        if text_content:
            text_content = text_content[:char_limit] + "... [truncated]"
        formatted_text += f"Text content from source: {text_content or ''}\n===\n"
        
        if include_raw_content:
            print("include_raw_content", source.get('raw_content'))
            # Using rough estimate of 4 characters per token
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"
        formatted_text.strip()   

        source = [
            {
                "type": "text",
                "text": formatted_text
            }
        ] + [{
            "type": "image_url",
            "image_url": {
                "url": segment
            }
        } for segment in source.get("screenshot_segments", [])[:images_per_source]]

        formatted_sources.extend(source)


    return formatted_sources

