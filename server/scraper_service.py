import os
import json
import time
import sys
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import re

class OnDemandScraper:
    def __init__(self):
        self.base_url = "https://gametora.com/umamusume"
        self.assets_dir = os.path.join(os.getcwd(), "assets")

    def setup_driver(self):
        """Setup Chrome driver with options for ad blocking and better scraping"""
        chrome_options = Options()

        # Basic headless options
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Anti-detection and performance options
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Ad blocking and content blocking
        adblock_path = os.path.join(os.getcwd(), 'adblock_extension')
        if os.path.exists(adblock_path):
            chrome_options.add_argument(f"--load-extension={adblock_path}")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Speed up loading
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")

        # Block common ad domains
        chrome_options.add_argument("--host-resolver-rules=MAP ads.gametora.com 127.0.0.1, MAP googlesyndication.com 127.0.0.1, MAP doubleclick.net 127.0.0.1")

        driver = webdriver.Chrome(options=chrome_options)

        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        return driver

    def character_exists(self, char_id, language="nested"):
        """Check if character data already exists in nested format"""
        # Use nested directory for single-file format
        char_dir = os.path.join(self.assets_dir, "character", "nested")

        # Find the slug from character_urls.json
        character_urls_file = os.path.join(self.assets_dir, "character", "character_urls.json")
        slug = None

        if os.path.exists(character_urls_file):
            try:
                with open(character_urls_file, 'r', encoding='utf-8') as f:
                    character_data = json.load(f)

                # Find the character by ID
                for character in character_data:
                    if character.get('slug', '').startswith(str(char_id)):
                        slug = character.get('slug')
                        break
            except:
                pass

        if slug:
            json_file = os.path.join(char_dir, f"{slug}.json")
            return os.path.exists(json_file)

        # Fallback: check if any file with the ID exists
        if os.path.exists(char_dir):
            for file in os.listdir(char_dir):
                if file.startswith(f"{char_id}-") and file.endswith(".json"):
                    return True
        return False

    def support_card_exists(self, card_id, language="nested"):
        """Check if support card data already exists in nested format"""
        # Use nested directory for single-file format
        card_dir = os.path.join(self.assets_dir, "support", "nested")

        # Find the slug from support_urls.json or support_card_urls.txt
        support_urls_file = os.path.join(self.assets_dir, "support", "support_urls.json")
        slug = None

        if os.path.exists(support_urls_file):
            try:
                with open(support_urls_file, 'r', encoding='utf-8') as f:
                    support_data = json.load(f)

                # Find the support card by ID
                for support in support_data:
                    if support.get('slug', '').startswith(str(card_id)):
                        slug = support.get('slug')
                        break
            except:
                pass

        # If not found in JSON, check the text file
        if not slug:
            try:
                with open("support_card_urls.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and str(card_id) in line:
                            slug = line.rstrip('/').split('/')[-1]
                            break
            except:
                pass

        if slug:
            json_file = os.path.join(card_dir, f"{slug}.json")
            return os.path.exists(json_file)

        # Fallback: check if any file with the ID exists
        if os.path.exists(card_dir):
            for file in os.listdir(card_dir):
                if file.startswith(f"{card_id}-") and file.endswith(".json"):
                    return True
        return False

    def scrape_character(self, char_id, language="nested"):
        """Scrape character data using the working scraper"""
        if self.character_exists(char_id, language):
            print(f"[SCRAPER] Character {char_id} already exists, skipping...")
            return True

        # Use the working character scraper
        try:
            from core.scrape_umamusume_character_events import scrape_character_complete

            # Construct the URL from character_urls.json
            character_urls_file = os.path.join(self.assets_dir, "character", "character_urls.json")
            character_url = None

            if os.path.exists(character_urls_file):
                with open(character_urls_file, 'r', encoding='utf-8') as f:
                    character_data = json.load(f)

                # Find the character by ID
                for character in character_data:
                    if character.get('slug', '').startswith(str(char_id)):
                        character_url = character.get('url')
                        break

            if not character_url:
                print(f"[SCRAPER] Could not find URL for character {char_id}")
                return False

            print(f"[SCRAPER] Using working scraper for character {char_id}")
            result = scrape_character_complete(character_url)

            if result:
                print(f"[SCRAPER] Successfully scraped character {char_id} using working scraper")
                return True
            else:
                print(f"[SCRAPER] Working scraper failed for character {char_id}")
                return False

        except Exception as e:
            print(f"[SCRAPER] Error using working scraper: {e}")
            return False

    def scrape_support_card(self, card_id, language="nested"):
        """Scrape support card data using the working scraper"""
        if self.support_card_exists(card_id, language):
            print(f"[SCRAPER] Support card {card_id} already exists, skipping...")
            return True

        # Use the working support card scraper
        try:
            # Import the working scraper functions
            sys.path.append(os.getcwd())
            
            # Import and use support scraper functions
            from core.scrape_umamusume_support_events import extract_support_events_with_tooltips, extract_japanese_support_events, combine_support_data

            # Construct the URL from support_urls.json
            support_urls_file = os.path.join(self.assets_dir, "support", "support_urls.json")
            support_url = None

            if os.path.exists(support_urls_file):
                with open(support_urls_file, 'r', encoding='utf-8') as f:
                    support_data = json.load(f)

                # Find the support card by ID
                for support in support_data:
                    if support.get('slug', '').startswith(str(card_id)):
                        support_url = support.get('url')
                        break

            if not support_url:
                print(f"[SCRAPER] Could not find URL for support card {card_id}")
                return False

            print(f"[SCRAPER] Using working scraper for support card {card_id}")

            # Setup driver and scrape
            driver = self.setup_driver()

            try:
                # Extract English events
                english_events = extract_support_events_with_tooltips(driver, support_url)

                # Extract Japanese events
                japanese_events = extract_japanese_support_events(driver, support_url)

                if not english_events and not japanese_events:
                    print(f"[SCRAPER] No events found for support card {card_id}")
                    return False

                # Combine data
                slug = support_url.rstrip('/').split('/')[-1]
                combined_events = combine_support_data(english_events, japanese_events, slug)

                # Save to nested directory for single file format
                card_dir = os.path.join(self.assets_dir, "support", "nested")
                os.makedirs(card_dir, exist_ok=True)

                # Create nested data structure with all information in one file
                nested_data = {
                    "support_id": slug,
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "summary": {
                        "english_events": sum(len(cat["events"]) for cat in english_events),
                        "japanese_events": sum(len(cat["events"]) for cat in japanese_events),
                        "combined_events": sum(len(cat["events"]) for cat in combined_events),
                        "total_categories": len(set([cat["category"] for cat in english_events + japanese_events]))
                    },
                    "data": {
                        "english": {
                            "events": english_events,
                            "total_events": sum(len(cat["events"]) for cat in english_events)
                        },
                        "japanese": {
                            "events": japanese_events,
                            "total_events": sum(len(cat["events"]) for cat in japanese_events)
                        },
                        "combined": {
                            "events": combined_events,
                            "total_events": sum(len(cat["events"]) for cat in combined_events)
                        }
                    }
                }

                # Save with slug name (nested format)
                filename = f"{slug}.json"
                filepath = os.path.join(card_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(nested_data, f, indent=2, ensure_ascii=False)

                print(f"[SCRAPER] Successfully saved support card {card_id} using nested format")
                print(f"[SCRAPER] File: {filepath}")
                return True

            finally:
                driver.quit()

        except Exception as e:
            print(f"[SCRAPER] Error using working scraper: {e}")
            return False

    def extract_character_data(self, driver, char_id):
        """Extract character data from the page"""
        try:
            character_data = {
                "character_id": char_id,
                "name": f"Character {char_id}",
                "events": [],
                "stats": {},
                "skills": [],
                "scraped_at": time.time(),
                "source": "gametora.com"
            }

            # Try to extract character name
            try:
                # Look for various possible selectors for character name
                name_selectors = [
                    ".character-name",
                    ".char-name",
                    "h1",
                    ".profile-name",
                    ".name"
                ]

                for selector in name_selectors:
                    try:
                        name_element = driver.find_element(By.CSS_SELECTOR, selector)
                        if name_element and name_element.text.strip():
                            character_data["name"] = name_element.text.strip()
                            break
                    except:
                        continue
            except:
                pass

            # Try to extract events
            try:
                # Look for event containers - try more comprehensive selectors
                event_selectors = [
                    ".character-event",
                    ".event",
                    ".event-item",
                    "[class*='event']",
                    ".story-event",
                    ".training-event",
                    ".scenario-event",
                    ".random-event",
                    ".support-event",
                    ".card-event",
                    ".event-container",
                    ".event-list",
                    ".events",
                    "[data-event]",
                    "[class*='story']",
                    "[class*='training']",
                    ".content",
                    ".main-content",
                    "article",
                    "section"
                ]

                print(f"[SCRAPER] Looking for events on page for character {char_id}...")
                page_source = driver.page_source
                print(f"[SCRAPER] Page source length: {len(page_source)}")

                for selector in event_selectors:
                    try:
                        event_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if event_elements:
                            print(f"[SCRAPER] Found {len(event_elements)} elements with selector: {selector}")
                            for i, event in enumerate(event_elements[:3]):  # Check first 3 elements
                                try:
                                    text = event.text.strip()
                                    if text:
                                        print(f"[SCRAPER] Element {i} text preview: {text[:200]}...")
                                except:
                                    pass

                            # Now try to extract actual events
                            for event in event_elements[:10]:  # Limit to first 10 events
                                try:
                                    event_data = {
                                        "name": "Unknown Event",
                                        "type": "character_event",
                                        "effects": "Unknown effects"
                                    }

                                    # Try to extract event name
                                    name_selectors = [".event-name", ".name", "h3", "h4", "strong", "h2", "h1", "b", "span"]
                                    for name_sel in name_selectors:
                                        try:
                                            name_elem = event.find_element(By.CSS_SELECTOR, name_sel)
                                            if name_elem and name_elem.text.strip():
                                                event_data["name"] = name_elem.text.strip()
                                                break
                                        except:
                                            continue

                                    # Try to extract event effects
                                    effect_selectors = [".event-effects", ".effects", ".description", "p", ".text", ".content", "div"]
                                    for effect_sel in effect_selectors:
                                        try:
                                            effect_elem = event.find_element(By.CSS_SELECTOR, effect_sel)
                                            if effect_elem and effect_elem.text.strip():
                                                event_data["effects"] = effect_elem.text.strip()
                                                break
                                        except:
                                            continue

                                    character_data["events"].append(event_data)
                                except:
                                    continue
                            break
                    except Exception as e:
                        print(f"[SCRAPER] Error with selector {selector}: {e}")
                        continue
                    except:
                        continue
            except:
                pass

            # If no events found, add a placeholder
            if not character_data["events"]:
                character_data["events"] = [{
                    "name": "Basic Training",
                    "type": "character_event",
                    "effects": "Provides basic stat training"
                }]

            return character_data

        except Exception as e:
            print(f"[SCRAPER] Error extracting character data: {e}")
            # Return basic data even if extraction fails
            return {
                "character_id": char_id,
                "name": f"Character {char_id}",
                "events": [{
                    "name": "Basic Training",
                    "type": "character_event",
                    "effects": "Provides basic stat training"
                }],
                "stats": {},
                "skills": [],
                "scraped_at": time.time(),
                "source": "gametora.com",
                "error": str(e)
            }

    def extract_support_card_data(self, driver, card_id):
        """Extract support card data from the page"""
        try:
            card_data = {
                "card_id": card_id,
                "name": f"Support Card {card_id}",
                "events": [],
                "stats": {},
                "skills": [],
                "scraped_at": time.time(),
                "source": "gametora.com"
            }

            # Try to extract card name
            try:
                # Look for various possible selectors for card name
                name_selectors = [
                    ".card-name",
                    ".support-card-name",
                    ".name",
                    "h1",
                    ".profile-name"
                ]

                for selector in name_selectors:
                    try:
                        name_element = driver.find_element(By.CSS_SELECTOR, selector)
                        if name_element and name_element.text.strip():
                            card_data["name"] = name_element.text.strip()
                            break
                    except:
                        continue
            except:
                pass

            # Try to extract events
            try:
                # Look for event containers
                event_selectors = [
                    ".card-event",
                    ".support-event",
                    ".event",
                    ".event-item",
                    "[class*='event']"
                ]

                for selector in event_selectors:
                    try:
                        event_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if event_elements:
                            for event in event_elements[:10]:  # Limit to first 10 events
                                try:
                                    event_data = {
                                        "name": "Unknown Event",
                                        "type": "support_event",
                                        "effects": "Unknown effects"
                                    }

                                    # Try to extract event name
                                    name_selectors = [".event-name", ".name", "h3", "h4", "strong"]
                                    for name_sel in name_selectors:
                                        try:
                                            name_elem = event.find_element(By.CSS_SELECTOR, name_sel)
                                            if name_elem and name_elem.text.strip():
                                                event_data["name"] = name_elem.text.strip()
                                                break
                                        except:
                                            continue

                                    # Try to extract event effects
                                    effect_selectors = [".event-effects", ".effects", ".description", "p"]
                                    for effect_sel in effect_selectors:
                                        try:
                                            effect_elem = event.find_element(By.CSS_SELECTOR, effect_sel)
                                            if effect_elem and effect_elem.text.strip():
                                                event_data["effects"] = effect_elem.text.strip()
                                                break
                                        except:
                                            continue

                                    card_data["events"].append(event_data)
                                except:
                                    continue
                            break
                    except:
                        continue
            except:
                pass

            # If no events found, add a placeholder
            if not card_data["events"]:
                card_data["events"] = [{
                    "name": "Support Training",
                    "type": "support_event",
                    "effects": "Provides support card training effects"
                }]

            return card_data

        except Exception as e:
            print(f"[SCRAPER] Error extracting support card data: {e}")
            # Return basic data even if extraction fails
            return {
                "card_id": card_id,
                "name": f"Support Card {card_id}",
                "events": [{
                    "name": "Support Training",
                    "type": "support_event",
                    "effects": "Provides support card training effects"
                }],
                "stats": {},
                "skills": [],
                "scraped_at": time.time(),
                "source": "gametora.com",
                "error": str(e)
            }

# Global scraper instance
scraper = OnDemandScraper()

def scrape_character_on_demand(char_id, language="nested"):
    """Scrape character if it doesn't exist"""
    return scraper.scrape_character(char_id, language)

def scrape_support_card_on_demand(card_id, language="nested"):
    """Scrape support card if it doesn't exist"""
    return scraper.scrape_support_card(card_id, language)
