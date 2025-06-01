import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

TOTAL_PAGES = 107
BASE_URL = "https://www.reelshort.com/movie-genres/all-movies/{}"

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

def scrape_page(driver, page_num):
    url = BASE_URL.format("" if page_num == 1 else page_num)
    print(f"\n🔄 Scraping page {page_num}...")
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
            print(f"⚠️ Error parsing movie block: {e}")
    return page_movies

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    all_movies = []
    page_views = []
    grand_total_views = 0

    try:
        for page in range(1, TOTAL_PAGES + 1):
            movies = scrape_page(driver, page)
            all_movies.extend(movies)

            page_total = sum(view for _, _, view in movies)
            grand_total_views += page_total

            page_views.append({'Page': page, 'TotalViews': page_total})
            print(f"✅ Page {page} - Total views: {page_total:,}")
            time.sleep(2)

    finally:
        driver.quit()

    # Save data
    df_movies = pd.DataFrame(all_movies, columns=["Page", "Title", "Views"])
    df_pages = pd.DataFrame(page_views)

    movie_filename = f"movie_views_{timestamp}.csv"
    page_filename = f"page_views_{timestamp}.csv"

    df_movies.to_csv(movie_filename, index=False, encoding="utf-8-sig")
    df_pages.to_csv(page_filename, index=False, encoding="utf-8-sig")

    # Print grand total
    print("\n🎉 Finished scraping.")
    print(f"📊 Total views across all pages: {grand_total_views:,}")
    print(f"💾 Movie data saved to: {movie_filename}")
    print(f"💾 Page summary saved to: {page_filename}")

if __name__ == "__main__":
    main()
