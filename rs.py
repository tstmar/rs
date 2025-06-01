import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

TOTAL_PAGES = 107
BASE_URL = "https://www.reelshort.com/movie-genres/all-movies/{}"

# Converts view counts like "214k" or "1.2M" to integers
def parse_view_count(view_str):
    try:
        view_str = view_str.lower().replace(",", "")
        if 'k' in view_str:
            return int(float(view_str.replace('k', '')) * 1000)
        elif 'm' in view_str:
            return int(float(view_str.replace('m', '')) * 1_000_000)
        return int(view_str)
    except:
        return 0

# Scrape a single page for movies
def scrape_page(driver, page_num):
    url = BASE_URL.format("" if page_num == 1 else page_num)
    print(f"\n🔄 Loading page {page_num}: {url}")
    driver.get(url)
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    movie_blocks = soup.select("div.flex.rounded-4px")

    page_movies = []
    for block in movie_blocks:
        try:
            title_tag = block.select_one(".line-clamp-2 a")
            view_tag = block.select_one(".flex.items-center")
            if not title_tag or not view_tag:
                continue
            title = title_tag.text.strip()
            views_text = view_tag.text.strip()
            views = parse_view_count(views_text)
            page_movies.append((page_num, title, views))
        except Exception as e:
            print(f"⚠️ Error parsing a movie block: {e}")
    return page_movies

# Main scraping function
def main():
    # Timestamp for output filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    all_movies = []
    page_views = []

    try:
        for page in range(1, TOTAL_PAGES + 1):
            movies = scrape_page(driver, page)
            all_movies.extend(movies)

            total_views = sum(view for _, _, view in movies)
            page_views.append({'Page': page, 'TotalViews': total_views})

            print(f"✅ Page {page} - Total views: {total_views}")
            #time.sleep(0.3)  # polite delay to avoid being blocked

    finally:
        driver.quit()

    # Save movie-level data
    movie_filename = f"movie_views_{timestamp}.csv"
    df_movies = pd.DataFrame(all_movies, columns=["Page", "Title", "Views"])
    df_movies.to_csv(movie_filename, index=False, encoding="utf-8-sig")

    # Save page-level summary
    page_filename = f"page_views_{timestamp}.csv"
    df_pages = pd.DataFrame(page_views)
    df_pages.to_csv(page_filename, index=False, encoding="utf-8-sig")

    print(f"\n✅ Data saved to:")
    print(f"  📁 {movie_filename}")
    print(f"  📁 {page_filename}")

if __name__ == "__main__":
    main()
