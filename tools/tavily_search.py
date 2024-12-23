from tavily import TavilyClient, AsyncTavilyClient
import asyncio
from langsmith import traceable
from typing import List, Union, Dict
import os
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
tavily_async_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@traceable
def tavily_search(query):
    """Search the web using the Tavily API."""
    return tavily_client.search(query, max_results=5, include_raw_content=True)

@traceable
async def tavily_search_async(search_queries, max_results=5, tavily_topic="general", tavily_days=30,):
    """Performs concurrent web searches using the Tavily API."""
    search_tasks = []
    
    for query in search_queries:
        if tavily_topic == "news":
            search_tasks.append(
                tavily_async_client.search(
                    query,
                    max_results=max_results,
                    include_raw_content=True,
                    topic=tavily_topic,
                    days=tavily_days
                )
            )
        else:
            search_tasks.append(
                tavily_async_client.search(
                    query,
                    max_results=max_results,
                    include_raw_content=True,
                    topic=tavily_topic,
                
            )
        )
        

    # Execute all searches concurrently
    search_docs = await asyncio.gather(*search_tasks)

    return search_docs


def get_unique_urls(search_response):
    if isinstance(search_response, dict):
        sources_list = search_response.get('results', [])
    elif isinstance(search_response, list):
        sources_list = []
        for response in search_response:
            sources_list.extend(response.get('results', []) if isinstance(response, dict) else response)
    
    # Extract and return unique URLs
    unique_urls = set()
    for source in sources_list:
        if url := source.get('url'):  # Using walrus operator to check and assign
            unique_urls.add(url)
    
    return list(unique_urls)
    

def deduplicate_and_format_sources(
    search_response: Union[Dict, List[Dict]],
    max_tokens_per_source: int,
    include_raw_content: bool = True
) -> str:
    """
    Takes either a single search response or list of responses from Tavily API and formats them.
    Limits the raw_content to approximately max_tokens_per_source.
    include_raw_content specifies whether to include the raw_content from Tavily in the formatted string.
    
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
    formatted_text = "Sources:\n\n"
    for source in unique_sources.values():
        formatted_text += f"Source {source.get('title', 'N/A')}:\n===\n"
        formatted_text += f"URL: {source.get('url', 'N/A')}\n===\n"
        formatted_text += f"Most relevant content from source: {source.get('content', 'N/A')}\n===\n"
        if include_raw_content:
            # Using rough estimate of 4 characters per token
            char_limit = max_tokens_per_source * 4
            raw_content = source.get('raw_content') or ''
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"
                
    return formatted_text.strip()