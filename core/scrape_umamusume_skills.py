import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
import re

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

def get_all_character_urls():
    """Get all character URLs from the local character_urls.json file"""
    print("🔍 Loading character URLs from character_urls.json...")

    try:
        with open('character_urls.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        character_urls = []
        for item in data:
            # Skip the profile list entry
            if item.get('name') == '> Character Profile List':
                continue

            url = item.get('url')
            if url and url.startswith('https://gametora.com/umamusume/characters/'):
                character_urls.append(url)

        print(f"📋 Found {len(character_urls)} character URLs in local file")
        return character_urls

    except FileNotFoundError:
        print("❌ character_urls.json not found. Falling back to web scraping...")
        # Fallback to original web scraping method
        try:
            response = requests.get("https://gametora.com/umamusume/characters")
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all character links
            character_links = soup.find_all('a', href=re.compile(r'/umamusume/characters/\d+'))

            character_urls = []
            for link in character_links:
                href = link.get('href')
                if href and href not in character_urls:
                    # Convert relative URL to absolute
                    if href.startswith('/'):
                        full_url = f"https://gametora.com{href}"
                    else:
                        full_url = href
                    character_urls.append(full_url)

            print(f"📋 Found {len(character_urls)} character URLs via web scraping")
            return character_urls

        except Exception as e:
            print(f"❌ Error getting character URLs: {e}")
            return []

    except Exception as e:
        print(f"❌ Error loading character URLs from file: {e}")
        return []

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
            # First attempt: regular click
            element.click()
            return True
        except Exception as e1:
            try:
                # Second attempt: JavaScript click
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e2:
                try:
                    # Third attempt: scroll into view and click
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    element.click()
                    return True
                except Exception as e3:
                    if attempt == max_attempts - 1:
                        print(f"   ❌ All click attempts failed: {e3}")
                        return False
                    else:
                        # Apply ad cleanup between attempts
                        periodic_ad_cleanup(driver)
                        time.sleep(1)
                        continue
    return False


def extract_english_events_with_tooltips(character_id, character_name, driver):
    """Extract English events by clicking buttons and getting tooltips"""
    english_events = []

    try:
        # Load the English version of the page
        character_url = f"https://gametora.com/umamusume/characters/{character_id}"
        english_url = character_url + "?lang=en"
        print(f"📡 Loading English page: {english_url}")
        driver.get(english_url)

        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "compatibility_viewer_item__8ZTXu"))
        )

        print("✅ English page loaded successfully")

        # Apply comprehensive ad blocking
        apply_ad_blocking(driver)

        # First, extract events WITHOUT choices (these are just listed, not buttons)
        print("\n🔍 Extracting Events Without Choices...")
        no_choice_events = extract_events_without_choices(driver)
        english_events.extend(no_choice_events)
        print(f"📋 Found {len(no_choice_events)} events without choices")

        # Find all event buttons (these have choices)
        print(f"\n🔍 Finding event buttons...")
        event_buttons = driver.find_elements(By.CLASS_NAME, "compatibility_viewer_item__8ZTXu")

        print(f"📊 Found {len(event_buttons)} event buttons")

        # Apply periodic ad cleanup before processing events
        periodic_ad_cleanup(driver)

        for i, button in enumerate(event_buttons):
            try:
                # Get the event name from the button text
                event_name = button.text.strip()
                if not event_name:
                    continue

                print(f"\n[*] English Event {i+1}: '{event_name}'")

                # Close any existing tooltips first - more aggressive approach
                try:
                    print(f"   [X] Closing any existing tooltips")
                    # Multiple methods to ensure tooltips are closed
                    driver.execute_script("""
                        // Close all tooltips by removing them from DOM
                        var tooltips = document.querySelectorAll('.tippy-box');
                        tooltips.forEach(function(tooltip) {
                            tooltip.remove();
                        });

                        // Also try clicking body
                        document.body.click();
                    """)
                    time.sleep(0.5)
                except Exception as e:
                    print(f"   [WARN] Error closing tooltips: {e}")

                # Use safe click method with multiple fallbacks
                print(f"   [+] Clicking button to expand tooltip")
                click_success = safe_click_element(driver, button)

                if click_success:
                    # Wait longer for tooltip to fully load and update
                    time.sleep(2)

                    # Verify tooltip is open and get fresh content
                    tooltip_visible = False
                    tooltip_content_text = ""

                    try:
                        tooltip_boxes = driver.find_elements(By.CLASS_NAME, "tippy-box")
                        for tooltip in tooltip_boxes:
                            if tooltip.is_displayed():
                                tooltip_visible = True
                                # Get the tooltip content to verify it's for this event
                                try:
                                    content = tooltip.text
                                    tooltip_content_text = content[:100]  # First 100 chars for verification
                                except:
                                    pass
                                break
                    except Exception as e:
                        print(f"   [WARN] Error checking tooltip visibility: {e}")

                    if tooltip_visible:
                        print(f"   [✓] Tooltip opened with content: '{tooltip_content_text}'")
                        tooltip_data = extract_tooltip_data(driver, event_name)

                        # More aggressive tooltip closing
                        try:
                            print(f"   [X] Closing tooltip")
                            driver.execute_script("""
                                // Remove all tooltips completely
                                var tooltips = document.querySelectorAll('.tippy-box, .tippy-content');
                                tooltips.forEach(function(tooltip) {
                                    tooltip.remove();
                                });

                                // Also try ESC key simulation
                                var event = new KeyboardEvent('keydown', {key: 'Escape'});
                                document.dispatchEvent(event);
                            """)
                            time.sleep(0.5)
                        except Exception as e:
                            print(f"   [WARN] Could not close tooltip: {e}")
                    else:
                        print(f"   [WARN] Tooltip did not open for {event_name}")
                        tooltip_data = {"choices": []}

                    # Periodic ad cleanup after successful interaction
                    periodic_ad_cleanup(driver)
                else:
                    print(f"   [ERROR] Could not click button for {event_name}")
                    tooltip_data = {"choices": []}
                    continue

                if tooltip_data and tooltip_data["choices"]:
                    print(f"   [+] Added {len(tooltip_data['choices'])} English choices")
                    english_events.append({
                        "name": event_name,
                        "type": "with_choices",
                        "choices": tooltip_data["choices"]
                    })
                else:
                    print(f"   [WARN] No choices found for {event_name}")

            except Exception as e:
                print(f"[ERROR] Error processing event {i}: {e}")
                continue

            # Periodic cleanup every 5 events to keep page clean
            if (i + 1) % 5 == 0:
                periodic_ad_cleanup(driver)

    except Exception as e:
        print(f"❌ Error loading English page: {e}")

    # Remove duplicates based on event name
    seen_names = set()
    deduplicated_events = []
    
    for event in english_events:
        event_name = event["name"]
        if event_name not in seen_names:
            seen_names.add(event_name)
            deduplicated_events.append(event)
        else:
            print(f"⚠️ Removed duplicate event: '{event_name}'")

    print(f"\n🧹 Deduplication complete: {len(english_events)} → {len(deduplicated_events)} events")
    
    return deduplicated_events

def extract_events_without_choices(driver):
    """Extract events that don't have choices (directly give stats)"""
    no_choice_events = []

    try:
        # Look for the specific section "Events Without Choices"
        # These events are listed as text after the section header

        # Find all elements that might contain the event lists
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Events Without Choices') or contains(text(), 'Events without choices')]")

        for element in all_elements:
            try:
                # Get the parent container
                parent = element.find_element(By.XPATH, "..")

                # Look for all text content in this section
                section_text = parent.text
                print(f"   📄 Section text found: {len(section_text)} characters")

                # Try to extract events from individual HTML elements instead of parsing concatenated text
                events_text = []

                # Look for div elements that might contain individual event names
                event_elements = parent.find_elements(By.TAG_NAME, "div")

                for elem in event_elements:
                    text = elem.text.strip()
                    if text and len(text) > 3 and text != "Events Without Choices":
                        # Check if this looks like an event name
                        # Event names are typically title case and don't contain too many numbers/symbols
                        if (text[0].isupper() and
                            not text.isupper() and  # Not all caps
                            len(text) < 50 and      # Reasonable length
                            not any(char.isdigit() for char in text) and  # No numbers
                            text.count('!') <= 1 and  # At most one exclamation
                            text.count('?') <= 1):   # At most one question mark
                            events_text.append(text)

                # If we didn't find events in individual elements, try parsing the concatenated text
                if not events_text:
                    # Parse the concatenated event names using known patterns
                    # Based on the HTML structure, events are concatenated without spaces
                    # We need to split them intelligently using common event name patterns

                    # First, remove the header
                    content = section_text.replace("Events Without Choices", "").strip()

                    # Known event names from gametora.com for Maruzensky
                    known_events = [
                        "Feeling Top Gear",
                        "Walk the Walk",
                        "To New Heights",
                        "A Fun Race",
                        "Bring It Virtual Race",
                        "Virtual Car Race Results",
                        "Master Trainer",
                        "The Coolest Spot",
                        "Totally New Feeling",
                        "Big Trouble!",
                        "Totally New",
                        "New Feeling",
                        "Shockingly Careless!?"
                    ]

                    # Try to match known events first
                    events_text = []
                    remaining_content = content

                    for event in known_events:
                        if event.replace(" ", "").replace("!", "").replace("?", "").replace(".", "") in remaining_content:
                            events_text.append(event)
                            # Remove the matched event from remaining content
                            remaining_content = remaining_content.replace(event.replace(" ", "").replace("!", "").replace("?", "").replace(".", ""), "", 1)

                    # If we didn't find many events with known patterns, try a different approach
                    if len(events_text) < 5:
                        events_text = []
                        # Use a more conservative splitting approach
                        # Look for patterns like: word + space + Capital word
                        words = []
                        current_word = ""
                        i = 0

                        while i < len(content):
                            char = content[i]

                            if char.isupper() and current_word and not current_word[-1].isupper():
                                # Check if this looks like a new event name
                                # Look ahead to see if there's a space followed by another capital
                                look_ahead = content[i:i+20] if i+20 < len(content) else content[i:]

                                if " " in look_ahead:
                                    space_idx = look_ahead.find(" ")
                                    if space_idx + 1 < len(look_ahead) and look_ahead[space_idx + 1].isupper():
                                        # This looks like "Word Word" pattern
                                        words.append(current_word)
                                        current_word = char
                                    else:
                                        current_word += char
                                else:
                                    current_word += char
                            else:
                                current_word += char

                            i += 1

                        if current_word:
                            words.append(current_word)

                        # Group words into likely event names
                        events_text = []
                        current_event = ""

                        for word in words:
                            if not current_event:
                                current_event = word
                            elif len(current_event + " " + word) < 50:  # Reasonable event name length
                                current_event += " " + word
                            else:
                                if current_event.strip():
                                    events_text.append(current_event.strip())
                                current_event = word

                        if current_event.strip():
                            events_text.append(current_event.strip())

                print(f"   📋 Found {len(events_text)} potential events")
                for i, event in enumerate(events_text[:5]):  # Show first 5
                    print(f"     {i+1}: '{event}'")

                # Filter and validate the events
                for event_name in events_text:
                    event_name = event_name.strip()
                    if event_name and len(event_name) > 2:
                        no_choice_events.append({
                            "name": event_name,
                            "type": "no_choice",
                            "effects": "Direct stat bonus (varies by event)"
                        })

            except Exception as e:
                print(f"❌ Error processing section: {e}")
                continue

    except Exception as e:
        print(f"❌ Error extracting no-choice events: {e}")

    return no_choice_events

def extract_tooltip_data(driver, event_name):
    """Extract tooltip data for an event with validation"""
    tooltip_data = {"choices": []}

    try:
        # Wait a moment for tooltip to stabilize
        time.sleep(0.5)

        # Look for visible tooltip - only process the first one
        tooltip_boxes = driver.find_elements(By.CLASS_NAME, "tippy-box")

        for tooltip in tooltip_boxes:
            if tooltip.is_displayed():
                try:
                    tooltip_content = tooltip.find_element(By.CLASS_NAME, "tippy-content")

                    # Validate that this tooltip is for the current event
                    tooltip_text = tooltip_content.text.lower()
                    event_name_lower = event_name.lower()

                    # Basic validation - tooltip should contain some reference to the event
                    if not any(word in tooltip_text for word in event_name_lower.split()):
                        print(f"   [WARN] Tooltip content doesn't match event '{event_name}'")
                        continue

                    # Get the full tooltip text content instead of looking for HTML table
                    tooltip_full_text = tooltip_content.text.strip()
                    print(f"   [✓] Tooltip opened with content: '{tooltip_full_text}'")

                    # Parse the plain text content
                    lines = tooltip_full_text.split('\n')
                    print(f"   [✓] Parsed {len(lines)} lines from tooltip")

                    # Skip the first line (event name) and process the rest
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

                    print(f"   📋 Extracted {len(tooltip_data['choices'])} choices from tooltip text")
                    if tooltip_data['choices']:
                        print(f"   📝 Choices found: {[choice['option'] for choice in tooltip_data['choices']]}")

                except NoSuchElementException:
                    pass  # No tooltip content

                break  # Only process the first visible tooltip

    except Exception as e:
        pass  # Tooltip extraction failed

    return tooltip_data

def extract_japanese_events_from_json(character_url):
    """Extract Japanese events from the page's JSON data"""
    japanese_events = []

    try:
        # Load the Japanese page
        print(f"📡 Loading Japanese page: {character_url}")
        response = requests.get(character_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for script tags containing JSON data
        script_tags = soup.find_all('script')

        for script in script_tags:
            if script.string and 'window.__NUXT__' in script.string:
                # Extract the JSON data
                script_content = script.string

                # Find the JSON object
                start_idx = script_content.find('{')
                end_idx = script_content.rfind('}') + 1

                if start_idx != -1 and end_idx != -1:
                    json_str = script_content[start_idx:end_idx]

                    try:
                        data = json.loads(json_str)

                        # Navigate to the events data
                        if 'data' in data and len(data['data']) > 0:
                            page_data = data['data'][0]

                            # Look for events in various possible locations
                            events_found = False

                            # Try different paths to find events
                            possible_paths = [
                                ['compatibilityViewer', 'events'],
                                ['events'],
                                ['character', 'events']
                            ]

                            for path in possible_paths:
                                current_data = page_data
                                for key in path:
                                    if isinstance(current_data, dict) and key in current_data:
                                        current_data = current_data[key]
                                    else:
                                        current_data = None
                                        break

                                if current_data and isinstance(current_data, list):
                                    for event in current_data:
                                        if isinstance(event, dict) and 'name' in event:
                                            japanese_events.append({
                                                "name": event['name'],
                                                "type": "japanese_fallback",
                                                "choices": event.get('choices', [])
                                            })
                                    events_found = True
                                    break

                            if events_found:
                                print(f"✅ Found Japanese event data")
                                break

                    except json.JSONDecodeError:
                        continue

        if not japanese_events:
            print("⚠️ No Japanese event data found in JSON")

    except Exception as e:
        print(f"❌ Error extracting Japanese events: {e}")

    return japanese_events

def combine_and_save_data(character_url, english_events, japanese_events):
    """Combine English and Japanese data, preferring English when available"""
    character_id = character_url.split('/')[-1]

    # Create organized folder structure
    base_dir = "assets/character"
    english_dir = os.path.join(base_dir, "english")
    japanese_dir = os.path.join(base_dir, "japanese")
    combined_dir = os.path.join(base_dir, "combined")

    os.makedirs(english_dir, exist_ok=True)
    os.makedirs(japanese_dir, exist_ok=True)
    os.makedirs(combined_dir, exist_ok=True)

    # Save English data separately
    english_data = {
        "character_id": character_id,
        "events": english_events,
        "total_events": len(english_events),
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    english_filepath = os.path.join(english_dir, f"{character_id}.json")
    with open(english_filepath, "w", encoding="utf-8") as f:
        json.dump(english_data, f, ensure_ascii=False, indent=2)

    # Save Japanese data separately
    japanese_data = {
        "character_id": character_id,
        "events": japanese_events,
        "total_events": len(japanese_events),
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    japanese_filepath = os.path.join(japanese_dir, f"{character_id}.json")
    with open(japanese_filepath, "w", encoding="utf-8") as f:
        json.dump(japanese_data, f, ensure_ascii=False, indent=2)

    # Create combined data structure
    combined_data = {
        "character_id": character_id,
        "english_events": english_events,
        "japanese_events": japanese_events,
        "total_english": len(english_events),
        "total_japanese": len(japanese_events),
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save combined data
    combined_filepath = os.path.join(combined_dir, f"{character_id}.json")
    with open(combined_filepath, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Saved organized data:")
    print(f"   📁 English: {english_filepath}")
    print(f"   📁 Japanese: {japanese_filepath}")
    print(f"   📁 Combined: {combined_filepath}")
    print(f"📊 English events: {len(english_events)}")
    print(f"📊 Japanese events: {len(japanese_events)}")

    return combined_data

def scrape_skill_data():
    """Main function to scrape Uma Musume skill data"""
    print("🎯 Starting Uma Musume Skill Data Scraper")
    print("=" * 60)

    driver = None
    all_skills = []

    try:
        driver = setup_driver()

        # Scrape skills from the main skills page
        skills_url = "https://gametora.com/umamusume/skills"
        print(f"📡 Loading skills page: {skills_url}")

        driver.get(skills_url)
        time.sleep(3)  # Wait for page to load

        # Apply ad blocking
        apply_ad_blocking(driver)

        # Extract skill data
        skills_data = extract_skill_data(driver)
        all_skills.extend(skills_data)

        print(f"✅ Successfully scraped {len(all_skills)} skills")

        # Save to skill/nested/skill_data.json
        save_skill_data(all_skills)

        return all_skills

    except Exception as e:
        print(f"❌ Error during skill scraping: {e}")
        return []

    finally:
        if driver:
            driver.quit()

def extract_skill_data(driver):
    """Extract skill data from the skills page"""
    skills = []

    try:
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # Try to find skills in table format first
        print("🔍 Looking for skills in table format...")
        table_skills = extract_skills_from_table(driver)
        if table_skills:
            skills.extend(table_skills)
            print(f"✅ Found {len(table_skills)} skills from table")
        else:
            print("⚠️ No skills found in table format, trying alternative methods...")

        # If no table skills found, try the original element-based approach
        if not skills:
            # Wait for skill elements to load
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "skill-item"))
                )
            except:
                pass  # Continue if no skill-item elements found

            # Find all skill items
            skill_elements = driver.find_elements(By.CLASS_NAME, "skill-item")

            print(f"📊 Found {len(skill_elements)} skill elements")

            for i, skill_elem in enumerate(skill_elements):
                try:
                    skill_data = extract_single_skill_data(skill_elem)
                    if skill_data:
                        skills.append(skill_data)
                        print(f"✅ Skill {i+1}: {skill_data.get('name', 'Unknown')}")

                    # Progress indicator
                    if (i + 1) % 10 == 0:
                        print(f"📈 Progress: {i+1}/{len(skill_elements)} skills processed")

                except Exception as e:
                    print(f"❌ Error extracting skill {i+1}: {e}")
                    continue

        # If still no skills, try alternative selectors
        if not skills:
            print("🔄 Trying alternative skill selectors...")
            alternative_selectors = [
                ".skill-card",
                ".skill-entry",
                "[data-skill]",
                ".skill-list-item",
                ".skill-row",
                "[data-skill-name]"
            ]

            for selector in alternative_selectors:
                try:
                    alt_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if alt_elements:
                        print(f"📊 Found {len(alt_elements)} skills with selector: {selector}")
                        for j, elem in enumerate(alt_elements):
                            try:
                                skill_data = extract_single_skill_data(elem)
                                if skill_data:
                                    skills.append(skill_data)
                                    print(f"✅ Alt Skill {j+1}: {skill_data.get('name', 'Unknown')}")
                            except Exception as e:
                                continue
                        break
                except Exception as e:
                    continue

        # If still no skills, try to extract from page text
        if not skills:
            print("🔄 Attempting text-based extraction...")
            page_text = driver.find_element(By.TAG_NAME, "body").text
            skills = extract_skills_from_text(page_text)

    except Exception as e:
        print(f"❌ Error extracting skill data: {e}")

    return skills

def extract_skills_from_table(driver):
    """Extract skills from table format on gametora skills page"""
    skills = []

    try:
        # First, try to extract skills directly from the page text
        # since the table might be dynamically generated
        print("🔍 Attempting direct text extraction from page...")
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Split the text into lines and look for skill patterns
        lines = page_text.split('\n')
        current_skill = None
        skill_description = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for skill names (contain rarity symbols or specific patterns)
            if ('◎' in line or '○' in line) and len(line) > 3:
                # Save previous skill if exists
                if current_skill and skill_description:
                    skill_data = create_skill_data_from_text(current_skill, skill_description)
                    if skill_data:
                        skills.append(skill_data)

                # Start new skill
                current_skill = line
                skill_description = ""
            elif current_skill and line and len(line) > 10:
                # This might be the description
                if not skill_description:
                    skill_description = line
                elif 'More' in line:
                    # "More" indicates end of description
                    pass
                else:
                    # Additional description line
                    skill_description += " " + line

        # Don't forget the last skill
        if current_skill and skill_description:
            skill_data = create_skill_data_from_text(current_skill, skill_description)
            if skill_data:
                skills.append(skill_data)

        print(f"✅ Extracted {len(skills)} skills from page text")

        # If text extraction didn't work well, try table parsing
        if len(skills) < 5:
            print("🔄 Text extraction found few skills, trying table parsing...")
            table_skills = extract_skills_from_html_table(driver)
            if table_skills:
                skills.extend(table_skills)

    except Exception as e:
        print(f"❌ Error extracting skills from table: {e}")

    return skills

def create_skill_data_from_text(skill_name, description):
    """Create skill data dictionary from text extraction"""
    try:
        # Determine skill type from name
        skill_type = "Unknown"
        if 'handed' in skill_name.lower():
            skill_type = "Track"
        elif 'track' in skill_name.lower():
            skill_type = "Track"
        elif 'recovery' in skill_name.lower():
            skill_type = "Recovery"
        elif 'acceleration' in skill_name.lower():
            skill_type = "Acceleration"
        elif 'toughness' in skill_name.lower():
            skill_type = "Toughness"
        elif 'speed' in skill_name.lower():
            skill_type = "Speed"
        elif 'stamina' in skill_name.lower():
            skill_type = "Stamina"
        elif 'power' in skill_name.lower():
            skill_type = "Power"
        elif 'guts' in skill_name.lower():
            skill_type = "Guts"
        elif 'wisdom' in skill_name.lower():
            skill_type = "Wisdom"

        # Determine rarity from symbols
        skill_rarity = "Normal"
        if '◎' in skill_name:
            skill_rarity = "Unique"
        elif '○' in skill_name:
            skill_rarity = "Rare"

        # Extract effects from description
        effects = extract_skill_effects_from_text(description)

        skill_data = {
            'name': skill_name.replace('◎', '').replace('○', '').strip(),
            'description': description,
            'type': skill_type,
            'rarity': skill_rarity,
            'effects': effects,
            'requirements': 'No specific requirements',
            'source': 'gametora.com'
        }

        return skill_data

    except Exception as e:
        print(f"❌ Error creating skill data from text: {e}")
        return None

def extract_skills_from_html_table(driver):
    """Extract skills from HTML table elements"""
    skills = []

    try:
        # Find all tables on the page
        tables = driver.find_elements(By.TAG_NAME, "table")

        for table in tables:
            try:
                rows = table.find_elements(By.TAG_NAME, "tr")

                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        skill_name = cells[0].text.strip()
                        skill_desc = cells[1].text.strip() if len(cells) > 1 else ""

                        if skill_name and len(skill_name) > 3:
                            skill_data = create_skill_data_from_text(skill_name, skill_desc)
                            if skill_data:
                                skills.append(skill_data)

            except Exception as e:
                continue

    except Exception as e:
        print(f"❌ Error extracting from HTML table: {e}")

    return skills

def extract_skill_effects_from_text(text):
    """Extract skill effects from text description"""
    effects = {}

    try:
        # Look for stat bonuses
        stat_patterns = {
            'speed': r'Speed\s*([+-]\d+)',
            'stamina': r'Stamina\s*([+-]\d+)',
            'power': r'Power\s*([+-]\d+)',
            'guts': r'Guts\s*([+-]\d+)',
            'wisdom': r'Wisdom\s*([+-]\d+)'
        }

        for stat, pattern in stat_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                effects[stat] = int(match.group(1))

        # Look for special effects
        special_effects = []
        if 'recovery' in text.lower():
            special_effects.append('recovery')
        if 'acceleration' in text.lower():
            special_effects.append('acceleration')
        if 'toughness' in text.lower():
            special_effects.append('toughness')
        if 'track' in text.lower():
            special_effects.append('track_adaptation')

        if special_effects:
            effects['special'] = special_effects

        # Look for performance modifiers
        if 'increase' in text.lower() or 'boost' in text.lower():
            effects['performance_modifier'] = 'positive'
        elif 'decrease' in text.lower() or 'reduce' in text.lower():
            effects['performance_modifier'] = 'negative'

    except Exception as e:
        print(f"⚠️ Error extracting skill effects from text: {e}")

    return effects

def extract_single_skill_data(skill_element):
    """Extract data from a single skill element"""
    skill_data = {}

    try:
        # Extract skill name
        name_selectors = ["h3", ".skill-name", ".name", "[data-name]"]
        for selector in name_selectors:
            try:
                name_elem = skill_element.find_element(By.CSS_SELECTOR, selector)
                skill_data['name'] = name_elem.text.strip()
                break
            except:
                continue

        # Extract skill description/effect
        desc_selectors = [".skill-description", ".description", ".effect", "p"]
        for selector in desc_selectors:
            try:
                desc_elem = skill_element.find_element(By.CSS_SELECTOR, selector)
                skill_data['description'] = desc_elem.text.strip()
                break
            except:
                continue

        # Extract skill type/category
        type_selectors = [".skill-type", ".type", ".category", "[data-type]"]
        for selector in type_selectors:
            try:
                type_elem = skill_element.find_element(By.CSS_SELECTOR, selector)
                skill_data['type'] = type_elem.text.strip()
                break
            except:
                continue

        # Extract skill stats/effects
        skill_data['effects'] = extract_skill_effects(skill_element)

        # Extract skill requirements/level info
        req_selectors = [".requirements", ".level", ".unlock", "[data-requirements]"]
        for selector in req_selectors:
            try:
                req_elem = skill_element.find_element(By.CSS_SELECTOR, selector)
                skill_data['requirements'] = req_elem.text.strip()
                break
            except:
                continue

        # Set default values if not found
        if not skill_data.get('name'):
            return None

        skill_data.setdefault('description', 'No description available')
        skill_data.setdefault('type', 'Unknown')
        skill_data.setdefault('effects', {})
        skill_data.setdefault('requirements', 'No requirements specified')

        return skill_data

    except Exception as e:
        print(f"❌ Error extracting single skill data: {e}")
        return None

def extract_skill_effects(skill_element):
    """Extract skill effects/stats from skill element"""
    effects = {}

    try:
        # Look for stat bonuses
        stat_patterns = {
            'speed': r'Speed\s*([+-]\d+)',
            'stamina': r'Stamina\s*([+-]\d+)',
            'power': r'Power\s*([+-]\d+)',
            'guts': r'Guts\s*([+-]\d+)',
            'wisdom': r'Wisdom\s*([+-]\d+)'
        }

        skill_text = skill_element.text

        for stat, pattern in stat_patterns.items():
            match = re.search(pattern, skill_text, re.IGNORECASE)
            if match:
                effects[stat] = int(match.group(1))

        # Look for special effects
        special_effects = []
        if 'recovery' in skill_text.lower():
            special_effects.append('recovery')
        if 'acceleration' in skill_text.lower():
            special_effects.append('acceleration')
        if 'toughness' in skill_text.lower():
            special_effects.append('toughness')

        if special_effects:
            effects['special'] = special_effects

    except Exception as e:
        print(f"⚠️ Error extracting skill effects: {e}")

    return effects

def extract_skills_from_text(page_text):
    """Fallback method to extract skills from page text"""
    skills = []

    try:
        # Split text into lines and look for skill-like patterns
        lines = page_text.split('\n')

        current_skill = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line looks like a skill name
            if (len(line) > 3 and len(line) < 50 and
                not any(char.isdigit() for char in line) and
                line[0].isupper()):

                # Save previous skill if it exists
                if current_skill.get('name'):
                    skills.append(current_skill)

                # Start new skill
                current_skill = {
                    'name': line,
                    'description': 'Extracted from page text',
                    'type': 'Unknown',
                    'effects': {},
                    'requirements': 'Unknown'
                }

            elif current_skill.get('name') and line.startswith(('Increases', 'Boosts', 'Recovers', 'Reduces')):
                # This might be a skill effect
                current_skill['description'] = line

        # Don't forget the last skill
        if current_skill.get('name'):
            skills.append(current_skill)

    except Exception as e:
        print(f"❌ Error in text-based skill extraction: {e}")

    return skills

def save_skill_data(skills):
    """Save skill data to skill/nested/skill_data.json"""
    try:
        # Create directory if it doesn't exist
        os.makedirs("skill/nested", exist_ok=True)

        # Prepare data structure
        skill_data = {
            "metadata": {
                "total_skills": len(skills),
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source": "gametora.com",
                "version": "1.0"
            },
            "skills": skills
        }

        # Save to JSON file
        filepath = "skill/nested/skill_data.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(skill_data, f, ensure_ascii=False, indent=2)

        print(f"💾 Skill data saved to: {filepath}")
        print(f"📊 Total skills saved: {len(skills)}")

        # Print summary
        skill_types = {}
        for skill in skills:
            skill_type = skill.get('type', 'Unknown')
            skill_types[skill_type] = skill_types.get(skill_type, 0) + 1

        print("📈 Skill Type Summary:")
        for skill_type, count in skill_types.items():
            print(f"   • {skill_type}: {count} skills")

    except Exception as e:
        print(f"❌ Error saving skill data: {e}")

def test_skill_scraping():
    """Test function to scrape a few skills and show results"""
    print("🧪 Testing skill scraping...")

    driver = None
    try:
        driver = setup_driver()
        skills_url = "https://gametora.com/umamusume/skills"
        driver.get(skills_url)
        time.sleep(3)

        apply_ad_blocking(driver)

        # Try to find skill elements
        skill_selectors = [
            ".skill-item",
            ".skill-card",
            ".skill-entry",
            "[data-skill]",
            ".skill-list-item"
        ]

        for selector in skill_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} skills with selector: {selector}")

                    # Show first few skills as examples
                    for i, elem in enumerate(elements[:3]):
                        try:
                            text = elem.text[:100] if elem.text else "No text"
                            print(f"   Skill {i+1}: {text}...")
                        except:
                            print(f"   Skill {i+1}: Could not extract text")

                    break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {e}")
                continue

        # If no skills found, show page structure
        if not any(driver.find_elements(By.CSS_SELECTOR, selector) for selector in skill_selectors):
            print("🔍 No skills found with standard selectors. Page structure:")
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:500]
                print(f"Page text preview: {body_text}...")
            except:
                print("Could not extract page text")

    except Exception as e:
        print(f"❌ Test failed: {e}")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    import sys

    print(f"🔍 Command line arguments: {sys.argv}")

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("🧪 Test mode - testing skill scraping...")
            test_skill_scraping()
        elif sys.argv[1] == "skills":
            print("🎯 Skills mode - scraping skill data...")
            scrape_skill_data()
        else:
            print("❓ Unknown mode. Use 'test' or 'skills'")
    else:
        print("🎯 Default mode - scraping skill data...")
        scrape_skill_data()
