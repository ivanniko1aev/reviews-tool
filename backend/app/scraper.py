import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_google_reviews(google_maps_url, max_reviews=20):
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no browser window)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Setup WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open the provided URL
    driver.get(google_maps_url)
    time.sleep(5)  # Wait for the page to load

    # Scroll down to load more reviews
    scrollable_div = driver.find_element(By.XPATH, '//div[@role="main"]')
    for _ in range(5):  # Adjust this to load more reviews if needed
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(2)

    html_content = driver.page_source
    driver.quit()

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    reviews = []

    # Find all review elements
    review_elements = soup.find_all('div', class_='jftiEf fontBodyMedium')
    for review in review_elements[:max_reviews]:
        # Extract author, rating, and content
        author = review.find('div', class_='d4r55')
        rating = review.find('span', class_='kvMYJc')
        content = review.find('span', class_='wiI7pd')

        # Append the review information to the list
        reviews.append({
            'author': author.get_text(strip=True) if author else 'N/A',
            'rating': rating.get('aria-label') if rating else 'N/A',
            'content': content.get_text(strip=True) if content else 'N/A'
        })

    return reviews

def save_reviews_to_csv(reviews):
    # Create a filename based on the current date and time
    filename = f"google_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["author", "rating", "content"])
        writer.writeheader()
        writer.writerows(reviews)
    return filename

if __name__ == "__main__":
    # Sample Google Maps URL and max reviews to scrape
    google_maps_url = 'https://maps.app.goo.gl/D6nFw3rgXDh6ieR67'
    max_reviews = 10

    # Scrape reviews
    reviews = get_google_reviews(google_maps_url, max_reviews)

    # Print reviews to console
    for review in reviews:
        print(f"Author: {review['author']}")
        print(f"Rating: {review['rating']}")
        print(f"Content: {review['content']}")
        print("-" * 40)

    # Save reviews to CSV
    csv_filename = save_reviews_to_csv(reviews)
    print(f"Reviews saved to {csv_filename}")
