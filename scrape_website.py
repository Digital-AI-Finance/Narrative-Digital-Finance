"""
Selenium scraper for SNSF Narrative Digital Finance website.
Extracts all content from the Wix-based page.
"""

import json
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
    """Configure Chrome WebDriver with headless options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def wait_for_wix_content(driver, timeout=20):
    """Wait for Wix dynamic content to load."""
    try:
        # Wait for main content container
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        # Additional wait for dynamic content
        time.sleep(5)
    except Exception as e:
        print(f"Warning: Timeout waiting for content: {e}")


def extract_text_content(driver):
    """Extract all text content from the page."""
    content = {
        "url": driver.current_url,
        "title": "",
        "sections": [],
        "all_text": [],
        "headings": [],
        "paragraphs": [],
        "links": []
    }

    # Get page title
    try:
        content["title"] = driver.title
    except:
        pass

    # Extract all headings
    for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        try:
            elements = driver.find_elements(By.TAG_NAME, tag)
            for elem in elements:
                text = elem.text.strip()
                if text:
                    content["headings"].append({"level": tag, "text": text})
        except:
            pass

    # Extract paragraphs
    try:
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        for p in paragraphs:
            text = p.text.strip()
            if text and len(text) > 10:
                content["paragraphs"].append(text)
    except:
        pass

    # Extract spans (Wix often uses spans for text)
    try:
        spans = driver.find_elements(By.TAG_NAME, "span")
        for span in spans:
            text = span.text.strip()
            if text and len(text) > 20:
                if text not in content["all_text"]:
                    content["all_text"].append(text)
    except:
        pass

    # Extract divs with text content
    try:
        divs = driver.find_elements(By.CSS_SELECTOR, "div[data-testid], div.font_0, div.font_7, div.font_8")
        for div in divs:
            text = div.text.strip()
            if text and len(text) > 20:
                if text not in content["all_text"]:
                    content["all_text"].append(text)
    except:
        pass

    # Try Wix-specific selectors
    wix_selectors = [
        "[data-hook='rich-text-container']",
        ".rich-text-container",
        "[data-mesh-id]",
        ".txtNew",
        ".font_0", ".font_5", ".font_7", ".font_8",
        "[data-testid='richTextElement']",
        ".wixui-rich-text__text"
    ]

    for selector in wix_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                text = elem.text.strip()
                if text and len(text) > 10:
                    if text not in content["all_text"]:
                        content["all_text"].append(text)
        except:
            pass

    # Extract links
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")
            text = link.text.strip()
            if href and text:
                content["links"].append({"text": text, "url": href})
    except:
        pass

    # Get full page text as fallback
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        full_text = body.text
        content["full_page_text"] = full_text
    except:
        pass

    return content


def scrape_website(url):
    """Main scraping function."""
    print(f"Scraping: {url}")

    driver = setup_driver()

    try:
        driver.get(url)
        print("Page loaded, waiting for dynamic content...")

        wait_for_wix_content(driver)

        print("Extracting content...")
        content = extract_text_content(driver)

        # Clean up duplicates
        content["all_text"] = list(set(content["all_text"]))
        content["paragraphs"] = list(set(content["paragraphs"]))

        return content

    finally:
        driver.quit()


def save_content(content, output_file):
    """Save extracted content to JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

    print(f"Content saved to: {output_path.absolute()}")
    return output_path


def main():
    url = "https://www.digital-finance-msca.com/snsf-narrative-digital-finance"
    output_file = Path(__file__).parent / "scraped_content.json"

    content = scrape_website(url)
    save_content(content, output_file)

    # Print summary
    print("\n--- Extraction Summary ---")
    print(f"Title: {content.get('title', 'N/A')}")
    print(f"Headings found: {len(content.get('headings', []))}")
    print(f"Paragraphs found: {len(content.get('paragraphs', []))}")
    print(f"Text blocks found: {len(content.get('all_text', []))}")
    print(f"Links found: {len(content.get('links', []))}")

    if content.get("full_page_text"):
        print(f"\nFull page text length: {len(content['full_page_text'])} characters")
        print("\n--- Full Page Text Preview (first 2000 chars) ---")
        print(content["full_page_text"][:2000])


if __name__ == "__main__":
    main()
