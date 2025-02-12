import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from database import save_reviews_to_db

async def get_google_reviews(google_maps_url, max_reviews=20):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(google_maps_url)
        print(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to retrieve content from {google_maps_url}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        reviews = []

        review_elements = soup.find_all('div', class_='jftiEf fontBodyMedium')
        for review in review_elements[:max_reviews]:
            author = review.find('div', class_='d4r55')
            rating = review.find('span', class_='kvMYJc')
            content = review.find('span', class_='wiI7pd')

            reviews.append({
                'author': author.get_text(strip=True) if author else 'N/A',
                'rating': rating.get('aria-label') if rating else 'N/A',
                'content': content.get_text(strip=True) if content else 'N/A'
            })
        return reviews


async def scrape_and_save_reviews(google_maps_url, user_id, db):
    reviews = await get_google_reviews(google_maps_url)
    await save_reviews_to_db(db, user_id, reviews)
