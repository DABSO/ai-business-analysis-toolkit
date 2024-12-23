from bs4 import BeautifulSoup
import requests
import csv
import os
import pandas as pd

def scrape_trustpilot_reviews(base_url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'accept-language': 'en-US,en;q=0.9'
    }
    payload = {
        'api_key': os.getenv("SCRAPER_API_KEY"),
        'render': 'true',
        'keep_headers': 'true',
    }
    
    try:
        pages_to_scrape = 10
        df = pd.DataFrame(columns=['Reviewer', 'Rating', 'Review', 'Date'])
        for page in range(1, pages_to_scrape):
            payload['url'] = f"{base_url}?page={page}"
            page_response = requests.get('https://api.scraperapi.com', params=payload, headers=headers)
            print(f"got response from page {page} length {len(page_response.content)}")
            page_soup = BeautifulSoup(page_response.content, 'html.parser')
            reviews = page_soup.find_all('div', {"class": "styles_reviewCardInner__EwDq2"})

            if len(reviews) == 0:
                break
            
            for review in reviews:
                reviewer = review.find("span", attrs={"class": "typography_heading-xxs__QKBS8"}).text
                
                rating = review.find("div", attrs={"class": "styles_reviewHeader__iU9Px"})["data-service-review-rating"]
                content_element = review.find("p", attrs={"class": "typography_body-l__KUYFJ"})
                content = content_element.text if content_element else 'None'
                date = review.find("p", attrs={"class":"typography_body-m__xgxZ_ typography_appearance-default__AAY17"}).text
                print(f"got reviewer {reviewer} rating {rating} content {content[:100]}... date {date}")
                df = df._append({'Reviewer': reviewer, 'Rating': rating, 'Review': content, 'Date': date}, ignore_index=True)
        print("Data Extraction Successful!")
        return df
    except Exception as e:
        print("An error occurred during scraping trustpilot reviews:", e)
        return None


def scrape_google_reviews(base_url: str):
    
    
    pass
