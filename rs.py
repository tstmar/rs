from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from datetime import datetime

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def get_total_pages(driver, base_url):
    driver.get(base_url)
    
    # Wait for pagination links to load by waiting for any <a> with page number
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/movie-genres/all-movies/']"))
    )

    # Collect all numbered <a> elements
    page_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/movie-genres/all-movies/']")
    page_numbers = []

    for link in page_links:
        text = link.text.strip()
        if text.isdigit():
            page_numbers.append(int(text))
    
    if not page_numbers:
        return 1  # fallback to 1 if failed

    total_pages = max(page_numbers)
    print(f"✅ Detected total pages: {total_pages}")
    return total_pages

def extract_movies_from_page(driver, url):
    driver.get(url)
    #time.sleep(2)
    movies_data = []
    movie_cards = driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-col.justify-between.overflow-hidden")

    for card in movie_cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, "a").text.strip()
            views = card.find_elements(By.CSS_SELECTOR, "div.flex.items-center span")[-1].text.strip()
            movies_data.append({"title": title, "views": views})
        except Exception:
            continue
    return movies_data

def convert_views(view_str):
    view_str = view_str.lower().replace(',', '')
    if 'k' in view_str:
        return int(float(view_str.replace('k', '')) * 1_000)
    elif 'm' in view_str:
        return int(float(view_str.replace('m', '')) * 1_000_000)
    elif view_str.isdigit():
        return int(view_str)
    return 0

def main():
    base_url = "https://www.reelshort.com/movie-genres/all-movies"
    driver = init_driver()

    try:
        total_pages = get_total_pages(driver, base_url)
        all_movies = []
        per_page_views = []
        total_views = 0

        for page in range(1, total_pages + 1):
            url = f"{base_url}/{page}" if page > 1 else base_url
            print(f"Scraping page {page}/{total_pages}...")
            movies = extract_movies_from_page(driver, url)
            all_movies.extend(movies)

            page_view_total = sum(convert_views(m["views"]) for m in movies)
            per_page_views.append({"page": page, "views": page_view_total})
            total_views += page_view_total

        print(f"\n🎉 Total view count across all pages: {total_views}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"reelshort_movies_{timestamp}.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["title", "views"])
            writer.writeheader()
            writer.writerows(all_movies)

        with open(f"reelshort_page_views_{timestamp}.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["page", "views"])
            writer.writeheader()
            writer.writerows(per_page_views)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
