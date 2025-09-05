import os
import json
import time
import re
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

def get_all_support_urls():
    """Get all support card URLs from file or web scraping as fallback"""
    print("🔍 Loading support card URLs from support_card_urls.txt...")
    
    try:
        # Try to load from existing file first
        with open("support_card_urls.txt", "r", encoding="utf-8") as f:
            support_urls = [line.strip() for line in f if line.strip()]
        
        if support_urls:
            print(f"📋 Found {len(support_urls)} support card URLs in local file")
            return support_urls
    except FileNotFoundError:
        print("❌ support_card_urls.txt not found. Falling back to web scraping...")
    
    # Fallback to web scraping like character scraper does
    print("🌐 Scraping support card URLs from gametora.com...")
    driver = setup_driver()
    try:
        support_urls = []
        
        # Visit support cards listing page
        driver.get("https://gametora.com/umamusume/supports")
        time.sleep(3)
        
        # Find all support card links
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/supports/']")
        for link in links:
            href = link.get_attribute('href')
            if href and href not in support_urls and '/supports/' in href:
                # Convert to full URL if needed
                if href.startswith('/'):
                    full_url = f"https://gametora.com{href}"
                    support_urls.append(full_url)
                elif href.startswith('https://gametora.com/umamusume/supports/'):
                    support_urls.append(href)
        
        print(f"🔍 Found {len(support_urls)} support card URLs via web scraping")
        
        # Save URLs to file for future use
        if support_urls:
            with open("support_card_urls.txt", "w", encoding="utf-8") as f:
                for url in support_urls:
                    f.write(f"{url}\n")
            print("💾 Saved support card URLs to support_card_urls.txt")
        
        return support_urls
    
    finally:
        driver.quit()

SUPPORT_DIR = os.path.join("assets", "support")
HEADERS = {"User-Agent": "Mozilla/5.0"}

os.makedirs(SUPPORT_DIR, exist_ok=True)

def setup_driver():
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
    chrome_options.add_argument(f"--load-extension={os.path.join(os.getcwd(), 'adblock_extension')}")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Speed up loading
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    # Block common ad domains
    chrome_options.add_argument("--host-resolver-rules=MAP ads.gametora.com 127.0.0.1, MAP googlesyndication.com 127.0.0.1, MAP doubleclick.net 127.0.0.1")

    # Additional ad blocking
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")

    driver = webdriver.Chrome(options=chrome_options)

    # Execute script to remove webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def apply_ad_blocking(driver):
    """Apply comprehensive ad blocking to prevent click interceptions"""
    try:
        # Comprehensive ad hiding script
        driver.execute_script("""
            // Hide common ad selectors
            var adSelectors = [
                '[class*="sticky"]',
                '[class*="footer"]',
                '[id*="ad"]',
                '[class*="publift"]',
                '[class*="ads"]',
                '[class*="banner"]',
                'iframe[src*="googlesyndication"]',
                'iframe[src*="doubleclick"]',
                'iframe[src*="facebook"]',
                'iframe[src*="amazon"]',
                'div[class*="ad-"]',
                'div[id*="ad-"]',
                '.ad-container',
                '.advertisement',
                '.sponsored',
                '[class*="popup"]',
                '[class*="modal"]',
                '[class*="overlay"]',
                'iframe[id*="google_ads"]',
                'iframe[title*="Advertisement"]',
                'iframe[aria-label*="Advertisement"]',
                'div[id*="sticky_footer"]',
                'div[class*="sticky-footer"]'
            ];

            adSelectors.forEach(function(selector) {
                var elements = document.querySelectorAll(selector);
                elements.forEach(function(el) {
                    el.style.display = 'none';
                    el.style.visibility = 'hidden';
                    el.style.position = 'absolute';
                    el.style.left = '-9999px';
                    el.style.zIndex = '-9999';
                    el.remove(); // Completely remove from DOM
                });
            });

            // Hide by ID patterns - more comprehensive
            var idsToHide = ['google_ads', 'ad_container', 'sticky_footer', 'floating_ad', 'ads', 'advertisement'];
            idsToHide.forEach(function(id) {
                var el = document.getElementById(id);
                if (el) {
                    el.style.display = 'none';
                    el.remove();
                }
            });

            // Hide all iframes with ad-related attributes
            var iframes = document.querySelectorAll('iframe');
            iframes.forEach(function(iframe) {
                var src = iframe.src || '';
                var id = iframe.id || '';
                var title = iframe.title || '';
                var ariaLabel = iframe.getAttribute('aria-label') || '';

                if (src.includes('googlesyndication') ||
                    src.includes('doubleclick') ||
                    src.includes('facebook') ||
                    src.includes('amazon') ||
                    src.includes('adsystem') ||
                    id.includes('google_ads') ||
                    id.includes('ad_') ||
                    title.includes('Advertisement') ||
                    ariaLabel.includes('Advertisement')) {
                    iframe.style.display = 'none';
                    iframe.remove();
                }
            });

            // Remove sticky/fixed positioned elements that might be ads
            var allElements = document.querySelectorAll('*');
            allElements.forEach(function(el) {
                var style = window.getComputedStyle(el);
                if (style.position === 'fixed' || style.position === 'sticky') {
                    var className = el.className || '';
                    var id = el.id || '';
                    if (className.includes('ad') || className.includes('banner') ||
                        className.includes('sticky') || id.includes('ad') ||
                        id.includes('google') || id.includes('ads')) {
                        el.style.display = 'none';
                        el.remove();
                    }
                }
            });

            console.log('Enhanced ad blocking script executed');
        """)
        print("[SHIELD] Enhanced comprehensive ad blocking applied")
    except Exception as e:
        print(f"⚠️ Could not apply ad blocking: {e}")

def periodic_ad_cleanup(driver):
    """Periodically clean up ads during scraping to prevent click interceptions"""
    try:
        driver.execute_script("""
            // Quick ad cleanup - focus on iframes and overlays
            var iframes = document.querySelectorAll('iframe');
            iframes.forEach(function(iframe) {
                var id = iframe.id || '';
                var title = iframe.title || '';
                if (id.includes('google_ads') || id.includes('ad_') ||
                    title.includes('Advertisement')) {
                    iframe.remove();
                }
            });

            // Remove any new sticky elements
            var stickies = document.querySelectorAll('[style*="position: fixed"], [style*="position: sticky"]');
            stickies.forEach(function(el) {
                if (el.offsetHeight > 50) { // Only remove large elements that might be ads
                    el.remove();
                }
            });
        """)
    except Exception as e:
        pass  # Silent fail for periodic cleanup

def safe_click_element(driver, element, max_attempts=3):
    """Safely click an element with multiple fallback strategies"""
    for attempt in range(max_attempts):
        try:
            # Scroll to element
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            # Click
            element.click()
            return True
        except Exception as e1:
            try:
                # JavaScript click
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e2:
                pass
    return False

def extract_tooltip_data_for_support(driver, is_english=True):
    """Extract tooltip data for support card events with character-like structure"""
    tooltip_data = {"name": "", "choices": []}
    try:
        # Wait a moment for tooltip to stabilize
        time.sleep(0.5)

        # Look for visible tooltip
        tooltip_boxes = driver.find_elements(By.CLASS_NAME, "tippy-box")

        for tooltip in tooltip_boxes:
            if tooltip.is_displayed():
                try:
                    print(f"   [✓] Found visible tooltip")
                    content = tooltip.find_element(By.CLASS_NAME, "tippy-content")
                    print(f"   [✓] Found tippy-content")

                    # Try to find the tooltip content - support cards might have different structure
                    tooltip_div = None
                    try:
                        # First try the original structure
                        tooltip_div = content.find_element(By.CLASS_NAME, "tooltips_tooltip__NxFYo")
                        print(f"   [✓] Found tooltips_tooltip__NxFYo")
                    except:
                        # Try alternative structure
                        try:
                            tooltip_div = content.find_element(By.CLASS_NAME, "tooltips_f90__JO4Qv")
                            print(f"   [✓] Found tooltips_f90__JO4Qv")
                        except:
                            print(f"   [WARN] Could not find tooltip div")
                            continue

                    # Extract heading
                    try:
                        heading = tooltip_div.find_element(By.CLASS_NAME, "tooltips_ttable_heading__DK4_X").text.strip()
                        print(f"   [✓] Found heading: '{heading}'")
                    except:
                        print(f"   [WARN] Could not find heading")
                        continue

                    # Extract cell content - parse the table structure from the HTML
                    try:
                        tooltip_div = content.find_element(By.CLASS_NAME, "tooltips_tooltip__NxFYo")
                        print(f"   [✓] Found tooltips_tooltip__NxFYo")

                        # Look for the table structure that contains options and effects
                        try:
                            table = tooltip_div.find_element(By.CLASS_NAME, "tooltips_ttable__K_X1k")
                            print(f"   [✓] Found tooltips table structure")

                            # Parse all table rows
                            rows = table.find_elements(By.CLASS_NAME, "tooltips_ttable_row__KWpFn")
                            print(f"   [✓] Found {len(rows)} table rows")

                            for i, row in enumerate(rows):
                                try:
                                    cells = row.find_elements(By.CLASS_NAME, "tooltips_ttable_cell__CQI5s")
                                    if len(cells) >= 2:
                                        option_name = cells[0].text.strip()
                                        effects_cell = cells[1]

                                        # Get all effect divs from the effects cell
                                        effect_divs = effects_cell.find_elements(By.TAG_NAME, "div")
                                        effects = [div.text.strip() for div in effect_divs if div.text.strip()]

                                        if option_name and effects:
                                            effects_text = " ".join(effects)
                                            tooltip_data["choices"].append({
                                                "option": option_name,
                                                "effects": effects_text
                                            })
                                            print(f"       ✅ Added choice: '{option_name}' with effects: '{effects_text}'")

                                except Exception as e:
                                    print(f"       [WARN] Error parsing row {i}: {e}")
                                    continue

                            print(f"   [✓] Total choices: {len(tooltip_data['choices'])}")

                        except:
                            print(f"   [WARN] Could not find table structure, trying alternative parsing...")

                            # Fallback: Try to find any cells with the expected class
                            try:
                                cell = tooltip_div.find_element(By.CLASS_NAME, "tooltips_ttable_cell__CQI5s")
                                print(f"   [DEBUG] Found cell element, checking contents...")

                                # Get the full cell text content and parse it
                                cell_full_text = cell.text.strip()
                                print(f"   [✓] Cell content: '{cell_full_text}'")

                                # Parse the plain text content
                                lines = cell_full_text.split('\n')
                                print(f"   [✓] Parsed {len(lines)} lines from cell")

                                # Skip the first line if it's just the event name, and process the rest
                                content_lines = lines[1:] if len(lines) > 1 else lines

                                current_choice = None
                                current_effects = []

                                for line in content_lines:
                                    line = line.strip()
                                    if not line:
                                        continue

                                    # Check if this line is a choice option
                                    is_choice_line = False
                                    choice_name = None

                                    # Check for various choice patterns
                                    if line in ["Top Option", "Bottom Option", "Left Option", "Right Option", "Top", "Bottom", "Left", "Right"]:
                                        is_choice_line = True
                                        choice_name = line
                                    elif line.startswith("Option ") and len(line) <= 10:
                                        is_choice_line = True
                                        choice_name = line
                                    elif len(line) <= 15 and not any(char in line for char in ["+", "-", "%", "→"]) and line.replace(" ", "").isalnum():
                                        # Short descriptive choice names
                                        is_choice_line = True
                                        choice_name = line

                                    if is_choice_line and choice_name:
                                        # Save previous choice if it exists
                                        if current_choice and current_effects:
                                            effects_text = " ".join(current_effects).strip()
                                            if effects_text:
                                                tooltip_data["choices"].append({
                                                    "option": current_choice,
                                                    "effects": effects_text
                                                })
                                                print(f"       ✅ Added choice: '{current_choice}' with effects: '{effects_text[:50]}...'")

                                        # Start new choice
                                        current_choice = choice_name
                                        current_effects = []
                                        print(f"       📝 Found choice: '{choice_name}'")
                                    elif current_choice and line:
                                        # This is an effect for the current choice
                                        current_effects.append(line)

                                # Don't forget the last choice
                                if current_choice and current_effects:
                                    effects_text = " ".join(current_effects).strip()
                                    if effects_text:
                                        tooltip_data["choices"].append({
                                            "option": current_choice,
                                            "effects": effects_text
                                        })
                                        print(f"       ✅ Added final choice: '{current_choice}' with effects: '{effects_text[:50]}...'")

                                print(f"   [✓] Total choices: {len(tooltip_data['choices'])}")

                                # If no structured choices found, check if it's a no-choice event
                                if not tooltip_data["choices"]:
                                    # Check if this event has direct effects (no choices)
                                    direct_text = cell.text.strip()
                                    if direct_text and heading:
                                        # Remove the heading from the effects text if it appears
                                        effects_only = direct_text.replace(heading, "").strip()
                                        if effects_only:
                                            # This is a no-choice event, store as single effect
                                            tooltip_data["choices"] = []  # No choices, this will be handled as no_choice event
                                            tooltip_data["direct_effects"] = effects_only
                                            print(f"   [✓] No-choice event with direct effects: '{effects_only}'")

                            except:
                                print(f"   [WARN] Could not find cell content - trying alternative selectors")

                                # Try alternative content selectors
                                try:
                                    # Look for any divs with text content
                                    all_divs = tooltip_div.find_elements(By.TAG_NAME, "div")
                                    text_content = []
                                    for div in all_divs:
                                        text = div.text.strip()
                                        if text and len(text) > 2:  # Filter out very short texts
                                            text_content.append(text)
                                    
                                    # Try to parse as "Option: Effect" format
                                    for text in text_content:
                                        if ":" in text and any(opt in text for opt in ["Top Option", "Bottom Option", "Option"]):
                                            parts = text.split(":", 1)
                                            if len(parts) == 2:
                                                tooltip_data["choices"].append({
                                                    "option": parts[0].strip(),
                                                    "effects": parts[1].strip()
                                                })
                                    
                                    print(f"   [ALT] Found {len(tooltip_data['choices'])} choices via alternative parsing")
                                except:
                                    print(f"   [WARN] Alternative selector also failed")
                                    continue

                    except Exception as e:
                        print(f"   [WARN] Could not extract cell content: {e}")
                        continue

                    tooltip_data["name"] = heading
                    break  # Found valid tooltip

                except Exception as e:
                    print(f"   [ERROR] Error processing tooltip: {e}")
                    continue

        if not tooltip_data["name"]:
            print("   [WARN] No tooltip name found")

    except Exception as e:
        print(f"   [ERROR] Error in tooltip extraction: {e}")

    return tooltip_data

def extract_support_events_with_tooltips(driver, url):
    """Extract support events by clicking buttons and getting tooltips"""
    events = []
    try:
        english_url = url + "?lang=en"
        print(f"📡 Loading English page: {english_url}")
        driver.get(english_url)

        # Wait for page to load - wait for buttons specifically
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "compatibility_viewer_item__8ZTXu"))
        )

        print("✅ English page loaded successfully")

        # Apply comprehensive ad blocking
        apply_ad_blocking(driver)

        # Scroll to ensure all content is loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # Find the 'Training Events' caption
        caption = None
        captions = driver.find_elements(By.CLASS_NAME, "supports_infobox_caption__ATGOw")
        for cap in captions:
            if "Training Events" in cap.text:
                caption = cap
                break

        if not caption:
            print("❌ No 'Training Events' caption found")
            return []

        # Find the container with event blocks
        container = None
        # Use XPath to find the next div sibling that contains eventhelper_elist__2IFwX
        try:
            container_xpath = "//div[@class='supports_infobox_caption__ATGOw' and contains(text(), 'Training Events')]/following-sibling::div"
            container = driver.find_element(By.XPATH, container_xpath)
        except:
            print("❌ Container not found via XPath")

        if not container:
            # Fallback: find all event buttons directly
            print("🔄 Using fallback method for event buttons")
            event_buttons = driver.find_elements(By.CLASS_NAME, "compatibility_viewer_item__8ZTXu")
            event_list = []
            for i, button in enumerate(event_buttons):
                try:
                    event_name = button.text.strip()
                    if not event_name:
                        continue

                    print(f"\n[*] English Event {i+1}: '{event_name}'")

                    # Close any existing tooltips
                    try:
                        driver.execute_script("""
                            var tooltips = document.querySelectorAll('.tippy-box');
                            tooltips.forEach(function(tooltip) { tooltip.remove(); });
                            document.body.click();
                        """)
                        time.sleep(0.5)
                    except:
                        pass

                    # Click button
                    click_success = safe_click_element(driver, button)
                    if click_success:
                        time.sleep(1.5)
                        tooltip_data = extract_tooltip_data_for_support(driver, is_english=True)
                        if tooltip_data["name"] and (tooltip_data["choices"] or tooltip_data.get("direct_effects")):
                            # Create event structure matching character events
                            if tooltip_data["choices"]:
                                # Event with choices
                                event_list.append({
                                    "name": tooltip_data["name"],
                                    "type": "with_choices",
                                    "choices": tooltip_data["choices"]
                                })
                                print(f"   [+] Added event with {len(tooltip_data['choices'])} choices")
                            elif tooltip_data.get("direct_effects"):
                                # Event without choices (direct effects)
                                event_list.append({
                                    "name": tooltip_data["name"],
                                    "type": "no_choice",
                                    "effects": tooltip_data["direct_effects"]
                                })
                                print(f"   [+] Added no-choice event with direct effects")
                        else:
                            print(f"   [WARN] No valid data found for {event_name}")
                    else:
                        print(f"   [ERROR] Could not click button for {event_name}")

                except Exception as e:
                    print(f"[ERROR] Error processing event {i}: {e}")
                    continue

            if event_list:
                events.append({
                    "category": "Training Events",
                    "events": event_list
                })
            return events

        # Parse blocks
        blocks = container.find_elements(By.CLASS_NAME, "eventhelper_elist__2IFwX")
        print(f"📊 Found {len(blocks)} event blocks")

        for block in blocks:
            try:
                category_div = block.find_element(By.CLASS_NAME, "sc-fc6527df-0")
                category_name = category_div.text.strip()
            except:
                category_name = "Unknown"

            event_buttons = block.find_elements(By.CLASS_NAME, "compatibility_viewer_item__8ZTXu")
            event_list = []

            print(f"📊 Processing {len(event_buttons)} buttons in category '{category_name}'")

            for i, button in enumerate(event_buttons):
                try:
                    event_name = button.text.strip()
                    if not event_name:
                        continue

                    print(f"\n[*] English Event {i+1}: '{event_name}'")

                    # Close any existing tooltips
                    try:
                        driver.execute_script("""
                            var tooltips = document.querySelectorAll('.tippy-box');
                            tooltips.forEach(function(tooltip) { tooltip.remove(); });
                            document.body.click();
                        """)
                        time.sleep(0.5)
                    except:
                        pass

                    # Click button
                    click_success = safe_click_element(driver, button)
                    if click_success:
                        time.sleep(1.5)

                        # Debug: Check if tooltip opened
                        tooltip_boxes = driver.find_elements(By.CLASS_NAME, "tippy-box")
                        visible_tooltips = [t for t in tooltip_boxes if t.is_displayed()]
                        print(f"   [DEBUG] Found {len(tooltip_boxes)} tooltips, {len(visible_tooltips)} visible")

                        tooltip_data = extract_tooltip_data_for_support(driver, is_english=True)
                        if tooltip_data["name"] and (tooltip_data["choices"] or tooltip_data.get("direct_effects")):
                            # Create event structure matching character events
                            if tooltip_data["choices"]:
                                # Event with choices
                                event_list.append({
                                    "name": tooltip_data["name"],
                                    "type": "with_choices",
                                    "choices": tooltip_data["choices"]
                                })
                                print(f"   [+] Added event with {len(tooltip_data['choices'])} choices")
                            elif tooltip_data.get("direct_effects"):
                                # Event without choices (direct effects)
                                event_list.append({
                                    "name": tooltip_data["name"],
                                    "type": "no_choice",
                                    "effects": tooltip_data["direct_effects"]
                                })
                                print(f"   [+] Added no-choice event with direct effects")
                        else:
                            print(f"   [WARN] No valid data found for {event_name}")
                    else:
                        print(f"   [ERROR] Could not click button for {event_name}")

                except Exception as e:
                    print(f"[ERROR] Error processing event {i}: {e}")
                    continue

            if event_list:
                events.append({
                    "category": category_name,
                    "events": event_list
                })

    except Exception as e:
        print(f"❌ Error extracting events: {e}")

    return events

def extract_japanese_support_events(driver, url):
    """Extract Japanese support events with choices from the page structure"""
    events = []
    try:
        print(f"📡 Loading Japanese page: {url}")
        driver.get(url)

        # Wait for page to load - wait for buttons specifically
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "compatibility_viewer_item__8ZTXu"))
        )

        print("✅ Japanese page loaded successfully")

        # Apply comprehensive ad blocking
        apply_ad_blocking(driver)

        # Scroll to ensure all content is loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

        # Find the 'Training Events' caption
        caption = None
        captions = driver.find_elements(By.CLASS_NAME, "supports_infobox_caption__ATGOw")
        for cap in captions:
            if "Training Events" in cap.text:
                caption = cap
                break

        if not caption:
            print("❌ No 'Training Events' caption found")
            return []

        # Find the container with event blocks
        container = None
        try:
            container_xpath = "//div[@class='supports_infobox_caption__ATGOw' and contains(text(), 'Training Events')]/following-sibling::div"
            container = driver.find_element(By.XPATH, container_xpath)
        except:
            print("❌ Container not found via XPath")

        if not container:
            # Fallback: find all event buttons directly
            print("🔄 Using fallback method for Japanese event buttons")
            event_buttons = driver.find_elements(By.CLASS_NAME, "compatibility_viewer_item__8ZTXu")
            event_list = []
            for i, button in enumerate(event_buttons):
                try:
                    event_name = button.text.strip()
                    if not event_name:
                        continue

                    print(f"\n[*] Japanese Event {i+1}: '{event_name}'")

                    # Close any existing tooltips
                    try:
                        driver.execute_script("""
                            var tooltips = document.querySelectorAll('.tippy-box');
                            tooltips.forEach(function(tooltip) { tooltip.remove(); });
                            document.body.click();
                        """)
                        time.sleep(0.5)
                    except:
                        pass

                    # Click button
                    click_success = safe_click_element(driver, button)
                    if click_success:
                        time.sleep(1.5)
                        tooltip_data = extract_tooltip_data_for_support(driver, is_english=False)
                        if tooltip_data["name"] and (tooltip_data["choices"] or tooltip_data.get("direct_effects")):
                            # Create event structure matching character events
                            if tooltip_data["choices"]:
                                # Event with choices
                                event_list.append({
                                    "name": tooltip_data["name"],
                                    "type": "with_choices",
                                    "choices": tooltip_data["choices"]
                                })
                                print(f"   [+] Added event with {len(tooltip_data['choices'])} choices")
                            elif tooltip_data.get("direct_effects"):
                                # Event without choices (direct effects)
                                event_list.append({
                                    "name": tooltip_data["name"],
                                    "type": "no_choice",
                                    "effects": tooltip_data["direct_effects"]
                                })
                                print(f"   [+] Added no-choice event with direct effects")
                        else:
                            print(f"   [WARN] No valid data found for {event_name}")
                    else:
                        print(f"   [ERROR] Could not click button for {event_name}")

                except Exception as e:
                    print(f"[ERROR] Error processing event {i}: {e}")
                    continue

            if event_list:
                events.append({
                    "category": "Training Events",
                    "events": event_list
                })
            return events

        # Parse blocks
        blocks = container.find_elements(By.CLASS_NAME, "eventhelper_elist__2IFwX")
        print(f"📊 Found {len(blocks)} event blocks")

        for block in blocks:
            try:
                category_div = block.find_element(By.CLASS_NAME, "sc-fc6527df-0")
                category_name = category_div.text.strip()
            except:
                category_name = "Unknown"

            event_buttons = block.find_elements(By.CLASS_NAME, "compatibility_viewer_item__8ZTXu")
            event_list = []

            print(f"📊 Processing {len(event_buttons)} buttons in category '{category_name}'")

            for i, button in enumerate(event_buttons):
                try:
                    event_name = button.text.strip()
                    if not event_name:
                        continue

                    print(f"\n[*] Japanese Event {i+1}: '{event_name}'")

                    # Close any existing tooltips
                    try:
                        driver.execute_script("""
                            var tooltips = document.querySelectorAll('.tippy-box');
                            tooltips.forEach(function(tooltip) { tooltip.remove(); });
                            document.body.click();
                        """)
                        time.sleep(0.5)
                    except:
                        pass

                    # Click button
                    click_success = safe_click_element(driver, button)
                    if click_success:
                        time.sleep(1.5)

                        # Debug: Check if tooltip opened
                        tooltip_boxes = driver.find_elements(By.CLASS_NAME, "tippy-box")
                        visible_tooltips = [t for t in tooltip_boxes if t.is_displayed()]
                        print(f"   [DEBUG] Found {len(tooltip_boxes)} tooltips, {len(visible_tooltips)} visible")

                        tooltip_data = extract_tooltip_data_for_support(driver, is_english=False)
                        if tooltip_data["name"] and (tooltip_data["choices"] or tooltip_data.get("direct_effects")):
                            # Create event structure matching character events
                            if tooltip_data["choices"]:
                                # Event with choices
                                event_list.append({
                                    "name": tooltip_data["name"],
                                    "type": "with_choices",
                                    "choices": tooltip_data["choices"]
                                })
                                print(f"   [+] Added event with {len(tooltip_data['choices'])} choices")
                            elif tooltip_data.get("direct_effects"):
                                # Event without choices (direct effects)
                                event_list.append({
                                    "name": tooltip_data["name"],
                                    "type": "no_choice",
                                    "effects": tooltip_data["direct_effects"]
                                })
                                print(f"   [+] Added no-choice event with direct effects")
                        else:
                            print(f"   [WARN] No valid data found for {event_name}")
                    else:
                        print(f"   [ERROR] Could not click button for {event_name}")

                except Exception as e:
                    print(f"[ERROR] Error processing event {i}: {e}")
                    continue

            if event_list:
                events.append({
                    "category": category_name,
                    "events": event_list
                })

    except Exception as e:
        print(f"❌ Error extracting Japanese events: {e}")

    return events

def combine_support_data(english_events, japanese_events, support_id):
    """Combine English and Japanese data, preferring English when available"""
    combined_events = []

    # Create a mapping of Japanese events by name for quick lookup
    japanese_map = {}
    for cat in japanese_events:
        for event in cat["events"]:
            japanese_map[event["name"]] = event

    # Combine categories
    all_categories = set()
    for cat in english_events + japanese_events:
        all_categories.add(cat["category"])

    for category in all_categories:
        combined_event_list = []

        # Get English events for this category
        english_cat_events = []
        for cat in english_events:
            if cat["category"] == category:
                english_cat_events = cat["events"]
                break

        # Get Japanese events for this category
        japanese_cat_events = []
        for cat in japanese_events:
            if cat["category"] == category:
                japanese_cat_events = cat["events"]
                break

        # Create mapping of Japanese events by name
        japanese_cat_map = {event["name"]: event for event in japanese_cat_events}

        # Combine events
        for eng_event in english_cat_events:
            name = eng_event["name"]
            jap_event = japanese_cat_map.get(name)
            combined_event = {
                "name": name,
                "effects": eng_event.get("effects", []),
                "options": jap_event.get("options", []) if jap_event else []
            }
            combined_event_list.append(combined_event)

        # Add any Japanese-only events
        for jap_event in japanese_cat_events:
            name = jap_event["name"]
            if not any(e["name"] == name for e in english_cat_events):
                combined_event = {
                    "name": name,
                    "effects": [],
                    "options": jap_event.get("options", [])
                }
                combined_event_list.append(combined_event)

        if combined_event_list:
            combined_events.append({
                "category": category,
                "events": combined_event_list
            })

    return combined_events

def scrape_support_events():
    """Scrape all support card events using Selenium"""
    support_urls = get_all_support_urls()
    if not support_urls:
        print("❌ No support card URLs found!")
        return
    
    driver = setup_driver()
    try:
        for url in support_urls:
            slug = url.rstrip('/').split('/')[-1]
            print(f"🚀 Scraping {slug} ...")

            # Extract English events with tooltips (effects)
            english_events = extract_support_events_with_tooltips(driver, url)

            # Extract Japanese events with choices
            japanese_events = extract_japanese_support_events(driver, url)

            if not english_events and not japanese_events:
                print(f"❌ No events found for {slug}")
                continue

            # Create organized folder structure
            base_dir = os.path.join("assets", "support")
            # Create single nested directory for all data
            nested_dir = os.path.join(base_dir, "nested")
            os.makedirs(nested_dir, exist_ok=True)

            # Combine events for the main usage
            combined_events = combine_support_data(english_events, japanese_events, slug)

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

            # Save single nested file
            nested_filepath = os.path.join(nested_dir, f"{slug}.json")
            with open(nested_filepath, "w", encoding="utf-8") as f:
                json.dump(nested_data, f, ensure_ascii=False, indent=2)

            print(f"💾 Saved nested data for {slug}:")
            print(f"   • English: {len(english_events)} categories, {nested_data['data']['english']['total_events']} events")
            print(f"   • Japanese: {len(japanese_events)} categories, {nested_data['data']['japanese']['total_events']} events") 
            print(f"   • Combined: {len(combined_events)} categories, {nested_data['data']['combined']['total_events']} events")
            print(f"   • Single file saved: {nested_filepath}")
            time.sleep(1)  # Be polite to the server

    except Exception as e:
        print(f"❌ Error during scraping: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    print(f"🔍 Command line arguments: {sys.argv}")

    if len(sys.argv) > 1 and sys.argv[1] == "bulk":
        print("🚀 Bulk mode detected - starting bulk scraping...")
        scrape_support_events()
    elif len(sys.argv) > 1 and sys.argv[1].startswith("http"):
        print("📝 Single mode - scraping specified support card...")
        # Test with specified URL
        url = sys.argv[1]
        slug = url.rstrip('/').split('/')[-1]
        print(f"Testing with {slug}...")
        driver = setup_driver()
        try:
            english_events = extract_support_events_with_tooltips(driver, url)
            japanese_events = extract_japanese_support_events(driver, url)

            if english_events or japanese_events:
                print("✅ Test successful!")
                print(f"English events: {sum(len(cat['events']) for cat in english_events)}")
                print(f"Japanese events: {sum(len(cat['events']) for cat in japanese_events)}")
            else:
                print("❌ Test failed - no events found")
        finally:
            driver.quit()
    else:
        print("📝 Single mode - scraping first support card...")
        # Test with first support card
        support_urls = get_all_support_urls()
        if support_urls:
            url = support_urls[0]
            slug = url.rstrip('/').split('/')[-1]
            print(f"Testing with {slug}...")
            driver = setup_driver()
            try:
                english_events = extract_support_events_with_tooltips(driver, url)
                japanese_events = extract_japanese_support_events(driver, url)

                if english_events or japanese_events:
                    print("✅ Test successful!")
                    print(f"English events: {sum(len(cat['events']) for cat in english_events)}")
                    print(f"Japanese events: {sum(len(cat['events']) for cat in japanese_events)}")
                else:
                    print("❌ Test failed - no events found")
            finally:
                driver.quit()
        else:
            print("❌ No support card URLs found!")
