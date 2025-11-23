import time
import pickle
from datetime import datetime

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os

# ----------------------------------------------------------
# LOAD TEMP INSTAGRAM USER CREDS
# ----------------------------------------------------------
load_dotenv()
TEMP_USER = os.getenv("IG_USER")
TEMP_PASS = os.getenv("IG_PASS")

COOKIE_FILE = "ig_cookies.pkl"
IG_LOGIN_URL = "https://www.instagram.com/accounts/login/"

# ----------------------------------------------------------
# BRAVE BROWSER SETUP
# ----------------------------------------------------------
def get_brave_driver():
    options = uc.ChromeOptions()
    options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    driver = uc.Chrome(options=options)
    real_quit = driver.quit

    def safe_quit():
        try:
            real_quit()
        except:
            pass

    driver.quit = safe_quit
    return driver

# ----------------------------------------------------------
# LOGIN + COOKIES HANDLING
# ----------------------------------------------------------
def login_instagram(driver):
    driver.get(IG_LOGIN_URL)
    time.sleep(5)

    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "rb") as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)

            driver.get("https://www.instagram.com/")
            time.sleep(5)
            print("✔ Logged in using saved cookies")
            return
        except Exception as e:
            print("⚠ Failed to load cookies, logging in normally.", e)

    print("🔐 Logging in using temp Instagram account...")
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(TEMP_USER)
    password_input.send_keys(TEMP_PASS)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(10)

    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("✔ Login success — Cookies saved")

# ----------------------------------------------------------
# EXTRACT POST METADATA
# ----------------------------------------------------------
def extract_post_info(soup):
    try:
        og_url = soup.find("meta", property="al:android:url")["content"]
        post_id = og_url.split("media?id=")[-1]
    except:
        post_id = "UNKNOWN"

    caption = ""
    caption_tag = soup.find("meta", property="og:description")
    if caption_tag:
        caption = caption_tag.get("content", "")

    try:
        upload_date = soup.find("time")["datetime"]
    except:
        upload_date = None

    return post_id, caption, upload_date

# ----------------------------------------------------------
# SCRAPE COMMENTS
# ----------------------------------------------------------
def scrape_instagram_post(post_url, max_comments=20):
    driver = get_brave_driver()
    login_instagram(driver)

    print("📄 Opening post:", post_url)
    driver.get(post_url)
    time.sleep(6)

    # Click the + (Load more comments) repeatedly
    for _ in range(10):
        try:
            load_more = driver.find_element(
                By.XPATH, "//div[.//svg[@aria-label='Load more comments']]"
            )
            driver.execute_script("arguments[0].click();", load_more)
            time.sleep(2)
        except:
            break

    # Scroll a bit to ensure lazy-loaded comments
    # for _ in range(5):
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    post_id, caption, upload_date = extract_post_info(soup)

    comments_data = []
    count = 0

    # Grab all comments
    comment_divs = soup.select("div.xt0psk2 > span._ap3a._aaco._aacu._aacx._aad7._aade")
    for tag in comment_divs:
        if count >= max_comments:
            break

        text = tag.get_text(strip=True)
        if not text:
            continue

        parent_li = tag.find_parent("li")
        username_tag = parent_li.find("a") if parent_li else None
        username = username_tag.get_text(strip=True) if username_tag else None
        time_tag = parent_li.find("time") if parent_li else None
        comment_time = time_tag["datetime"] if time_tag else None

        comments_data.append({
            "post_id": post_id,
            "username": username,
            "comment_text": text,
            "comment_publish_time": comment_time
        })
        count += 1

    df = pd.DataFrame(comments_data)
    driver.quit()
    return df, upload_date, caption, post_id

# ----------------------------------------------------------
# RUN SCRIPT
# ----------------------------------------------------------
df, upload_date, title, post_id = scrape_instagram_post(
    "https://www.instagram.com/p/DRBqIYZjEK8/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ==",
    max_comments=30
)

print(df.head())
print(f"\nPost ID: {post_id}\nTitle: {title}\nUpload Date: {upload_date}")
