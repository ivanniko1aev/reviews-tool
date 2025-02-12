import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import csv
import time
import random
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GoogleReviewScraper:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key not found in environment variables")
            
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _get_place_id(self, maps_url: str) -> Optional[str]:
        """Extract or fetch place ID from Google Maps URL."""
        try:
            print(f"Processing URL: {maps_url}")  # Debugging output
            # First try to extract from URL
            if 'place/' in maps_url:
                place_id = maps_url.split('place/')[1].split('/')[0]
                print(f"Extracted place ID from URL: {place_id}")  # Debugging output
                return place_id
            
            # If not in URL, try to search by query
            query = maps_url.split('/')[-1]
            search_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
            params = {
                'input': query,
                'inputtype': 'textquery',
                'fields': 'place_id',
                'key': self.api_key
            }
            
            response = self.session.get(search_url, params=params)
            print(f"API Response Status Code: {response.status_code}")  # Debugging output
            if response.status_code == 200:
                data = response.json()
                print(f"API Response Data: {data}")  # Debugging output
                if data.get('candidates'):
                    return data['candidates'][0]['place_id']
            else:
                print(f"API Response Error: {data.get('error_message', 'No error message provided')}")  # Debugging output
            return None
        except requests.RequestException as e:
            print(f"Error fetching place ID: {e}")
            return None

    def _fetch_reviews_api(self, place_id: str, max_reviews: int = 5, sort_order: str = 'most_relevant') -> List[Dict]:
        """Fetch reviews using Google Maps API endpoint."""
        reviews = []
        try:
            api_url = "https://maps.googleapis.com/maps/api/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,rating,formatted_phone_number,reviews',
                'key': self.api_key,
                'language': 'en',  # You can change this for different languages
            }
            
            response = self.session.get(api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK' and 'reviews' in data.get('result', {}):
                    # Sort reviews based on the specified order
                    if sort_order == 'newest':
                        reviews = sorted(data['result']['reviews'], key=lambda x: x['time'], reverse=True)[:max_reviews]
                    else:
                        reviews = data['result']['reviews'][:max_reviews]  # Default to most relevant
                else:
                    print(f"API Response Status: {data.get('status')}")
                    if 'error_message' in data:
                        print(f"Error message: {data['error_message']}")
            else:
                print(f"API Response Error: {data.get('error_message', 'No error message provided')}")  # Debugging output
        except requests.RequestException as e:
            print(f"Error fetching reviews: {e}")
        return reviews

    def _autocomplete_place_id(self, query: str) -> Optional[str]:
        """Fetch place ID using Place Autocomplete API."""
        try:
            autocomplete_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
            params = {
                'input': query,
                'key': self.api_key,
                'components': 'country:us'  # Adjust as necessary for your location
            }
            
            response = self.session.get(autocomplete_url, params=params)
            print(f"Autocomplete API Response Status Code: {response.status_code}")  # Debugging output
            if response.status_code == 200:
                data = response.json()
                print(f"Autocomplete API Response Data: {data}")  # Debugging output
                if data.get('predictions'):
                    place_id = data['predictions'][0]['place_id']
                    print(f"Retrieved place ID from autocomplete: {place_id}")  # Debugging output
                    return place_id
            else:
                print(f"Autocomplete API Response Error: {data.get('error_message', 'No error message provided')}")  # Debugging output
            return None
        except requests.RequestException as e:
            print(f"Error fetching place ID from autocomplete: {e}")
            return None

    def get_google_reviews(self, maps_url: str, max_reviews: int = 5) -> List[Dict]:
        """Main method to fetch Google reviews."""
        # Use the provided place ID directly for testing
        test_place_id = "ChIJ6ez5NNixj4ARSjlru4d7Vb8"
        reviews = self._fetch_reviews_api(test_place_id, max_reviews)
        
        # Format reviews
        formatted_reviews = []
        for review in reviews:
            # Debugging output to see the structure of the review
            print(f"Full Review Data: {review}")  # Print the entire review for debugging
            
            formatted_reviews.append({
                'author': review.get('author_name', 'A Google user'),  # Use 'author_name' as per API
                'rating': str(review.get('rating', 'N/A')),
                'content': review.get('text', 'N/A'),
                'relative_time': review.get('relative_time_description', 'N/A'),
                'time': review.get('time', None),
                'author_url': review.get('author_url', None),
                'language': review.get('language', None),
                'original_language': review.get('original_language', None),
                'profile_photo_url': review.get('profile_photo_url', None),
                'translated': review.get('translated', False)
            })

        return formatted_reviews

def save_reviews_to_csv(reviews: List[Dict]) -> str:
    """Save reviews to CSV file."""
    filename = f"google_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["author", "rating", "content", "time"])
        writer.writeheader()
        writer.writerows(reviews)
    return filename

if __name__ == "__main__":
    # Directly use a specific Place ID for testing
    test_place_id = "ChIJ6ez5NNixj4ARSjlru4d7Vb8"  # Replace with your desired place ID
    scraper = GoogleReviewScraper()
    
    # Fetch reviews using the specified place ID
    reviews = scraper._fetch_reviews_api(test_place_id, max_reviews=5)
    
    if reviews:
        print(f"Successfully retrieved {len(reviews)} reviews:")
        for review in reviews:
            print("\n---Review---")
            print(f"Full Review Data: {review}")  # Debugging output
            print(f"Author: {review.get('author_name', 'A Google user')}")  # Corrected key access
            print(f"Rating: {review.get('rating', 'N/A')}")
            print(f"Content: {review.get('text', 'N/A')[:100]}...")  # Show first 100 chars
            print(f"Time: {review.get('time', None)}")
    else:
        print("No reviews found")