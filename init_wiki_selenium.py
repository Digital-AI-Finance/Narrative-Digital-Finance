"""
Initialize GitHub Wiki using Selenium.
Creates the first wiki page automatically.
"""

import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Configure Chrome WebDriver (NOT headless - need to see login)."""
    chrome_options = Options()
    # NOT headless so user can log in if needed
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def init_wiki(driver, repo="Digital-AI-Finance/Narrative-Digital-Finance"):
    """Navigate to wiki and create initial page."""
    wiki_url = f"https://github.com/{repo}/wiki"
    print(f"Opening: {wiki_url}")

    driver.get(wiki_url)
    time.sleep(3)

    # Check if we need to create first page
    try:
        # Look for "Create the first page" button
        create_btn = driver.find_element(By.PARTIAL_LINK_TEXT, "Create the first page")
        print("Found 'Create the first page' button, clicking...")
        create_btn.click()
        time.sleep(2)
    except:
        print("Wiki may already be initialized or needs login")

    # Try to find the wiki editor
    try:
        # Wait for editor
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "gollum-editor-body"))
        )

        # Enter content
        editor = driver.find_element(By.ID, "gollum-editor-body")
        editor.clear()
        editor.send_keys("# Welcome to the Wiki\n\nThis wiki is being initialized.")

        # Find and click save button
        save_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save_btn.click()
        print("Page saved!")
        time.sleep(3)

    except Exception as e:
        print(f"Note: {e}")
        print("\nPlease manually create the first wiki page in the browser window.")
        print("After saving, press Enter here to continue...")
        input()

    return True


def main():
    print("=" * 60)
    print("GitHub Wiki Initialization via Selenium")
    print("=" * 60)

    driver = setup_driver()

    try:
        print("\nA browser window will open.")
        print("If you need to log in to GitHub, please do so.")
        print()

        init_wiki(driver)

        print("\nWiki initialization complete!")
        print("You can now close this script.")

    finally:
        print("\nBrowser will stay open for 30 seconds...")
        time.sleep(30)
        driver.quit()


if __name__ == "__main__":
    main()
