from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

def get_download_url(page_url: str) -> str:
    # Starta webbläsare (Chrome här, men kan vara Firefox)
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")   # kör utan GUI
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(page_url)

        # Klicka på download-knappen
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.download-btn.link-btn"))
        )
        btn.click()

        # Vänta tills länken syns
        link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.download-link"))
        )

        href = link.get_attribute("href")
        return href

    finally:
        driver.quit()


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Användning: python get_download_url.py <video-url>")
        sys.exit(1)
    url = sys.argv[1]
    dl_url = get_download_url(url)
    print("✅ Hittade download-URL:", dl_url)