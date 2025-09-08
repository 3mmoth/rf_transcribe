import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_chapters(url: str):
    """
    Hämtar alla kapitel/talar-tidsstämplar från en Quickchannel-sändning.
    
    Parametrar:
        url (str): Länk till sändningen (qcnl.tv eller play.norrkoping.se).
    
    Returnerar:
        list[dict]: En lista med dictionaries innehållande:
            - title (str)
            - start_time_seconds (float)
            - formatted_time (str, mm:ss)
    """
    service = Service()  # använder chromedriver i PATH
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)

    results = []

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        # 👉 Kolla om sidan innehåller en iframe
        try:
            iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            driver.switch_to.frame(iframe)
        except:
            pass  # Ingen iframe, använd huvudsidans spelare

        # Vänta tills videospelaren finns
        video_player = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "video-js")))

        # Klicka på play-knappen för att starta videon
        play_button = video_player.find_element(By.CLASS_NAME, "vjs-big-play-button")

        play_button.click()

        # Vänta lite så kapitelknapparna hinner laddas
        time.sleep(5)

        # Hämta alla kapitelknappar
        chapter_buttons = driver.find_elements(
            By.CSS_SELECTOR,
            "button.vjs-amber-chapter-marker.vjs-control.vjs-subchapter-marker"
        )

        for btn in chapter_buttons:
            title = btn.get_attribute("data-chapter-title").strip()
            start_time = float(btn.get_attribute("data-start-time"))
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            results.append({
                "title": title,
                "start_time_seconds": start_time,
                "formatted_time": f"{minutes:02d}:{seconds:02d}"
            })

    finally:
        driver.quit()

    return results