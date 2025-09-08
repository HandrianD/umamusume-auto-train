import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

def setup_driver():
    """Setup Chrome driver with options for scraping"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    return webdriver.Chrome(options=chrome_options)

def scrape_umamusume_skills():
    """Scrape all Uma Musume skills from gametora.com"""
    driver = None
    all_skills = []

    try:
        driver = setup_driver()

        # Skills page URL
        skills_url = "https://gametora.com/umamusume/skills"
        print(f"🔍 Loading skills page: {skills_url}")

        driver.get(skills_url)

        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "skills_table_row_ja__XXxOj"))
        )

        print("✅ Skills page loaded successfully")

        # Apply ad blocking
        driver.execute_script("""
            var adSelectors = ['[class*="ad"]', '[id*="ad"]', 'iframe', '.advertisement'];
            adSelectors.forEach(function(selector) {
                var elements = document.querySelectorAll(selector);
                elements.forEach(function(el) { el.remove(); });
            });
        """)

        # Scroll to load all skills
        print("📜 Scrolling to load all skills...")
        last_height = driver.execute_script("return document.body.scrollHeight")

        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print("✅ All skills loaded")

        # Find all skill rows using the exact class from your HTML
        skill_rows = driver.find_elements(By.CLASS_NAME, "skills_table_row_ja__XXxOj")

        print(f"📊 Found {len(skill_rows)} skill entries")

        for i, row in enumerate(skill_rows):
            try:
                skill_data = {}

                # Extract skill icon and ID from img src
                try:
                    img_element = row.find_element(By.TAG_NAME, "img")
                    icon_src = img_element.get_attribute("src")

                    # Extract skill ID from icon URL pattern: /images/umamusume/skill_icons/utx_ico_skill_10011.png
                    if "skill_icons/utx_ico_skill_" in icon_src:
                        skill_id_match = re.search(r'utx_ico_skill_(\d+)\.png', icon_src)
                        if skill_id_match:
                            skill_data['id'] = skill_id_match.group(1)
                            skill_data['icon_url'] = icon_src
                except Exception as e:
                    print(f"   ⚠️ Could not extract icon for skill {i+1}: {e}")

                # Extract Japanese name using the exact class from your HTML
                try:
                    jp_name_element = row.find_element(By.CLASS_NAME, "skills_table_jpname__5TTkO")
                    skill_data['name_jp'] = jp_name_element.text.strip()
                except Exception as e:
                    print(f"   ⚠️ Could not extract JP name for skill {i+1}: {e}")

                # Extract English description using the exact class from your HTML
                try:
                    desc_element = row.find_element(By.CLASS_NAME, "skills_table_desc__NzNzY")
                    skill_data['description_en'] = desc_element.text.strip()
                except Exception as e:
                    print(f"   ⚠️ Could not extract description for skill {i+1}: {e}")

                # Set English name (for now, use Japanese name as fallback)
                if 'name_jp' in skill_data:
                    skill_data['name_en'] = skill_data['name_jp']

                # Add metadata
                skill_data['scraped_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
                skill_data['source'] = "gametora.com"

                # Only add if we have essential data
                if skill_data.get('name_jp') and skill_data.get('id'):
                    all_skills.append(skill_data)
                    print(f"✅ Skill {i+1}: {skill_data['name_jp']} (ID: {skill_data['id']})")
                else:
                    print(f"⚠️ Skipping incomplete skill {i+1}")

            except Exception as e:
                print(f"❌ Error processing skill {i+1}: {e}")
                continue

        print(f"\n📊 Successfully extracted {len(all_skills)} skills")

    except Exception as e:
        print(f"❌ Error during skill scraping: {e}")

    finally:
        if driver:
            driver.quit()

    return all_skills

def save_skills_to_json(skills_data):
    """Save skills data to assets/skill/nested/skill_data.json"""

    # Create directory structure
    output_dir = "assets/skill/nested"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "skill_data.json")

    # Organize data structure
    organized_data = {
        "metadata": {
            "total_skills": len(skills_data),
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "gametora.com",
            "version": "1.0"
        },
        "skills": skills_data
    }

    # Save to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(organized_data, f, ensure_ascii=False, indent=2)

    print(f"💾 Skills data saved to: {output_file}")
    print(f"📊 Total skills saved: {len(skills_data)}")

    return output_file

def main():
    """Main function to scrape and save skills data"""
    print("🎯 Starting Uma Musume Skills Scraper")
    print("=" * 50)

    # Scrape skills data
    skills_data = scrape_umamusume_skills()

    if skills_data:
        # Save to JSON file
        output_file = save_skills_to_json(skills_data)

        print("\n🎉 SUCCESS! Skills scraping completed!")
        print(f"📁 Data saved to: {output_file}")
        print(f"📊 Skills extracted: {len(skills_data)}")

        # Show sample of extracted data
        if skills_data:
            print("\n📝 Sample extracted skills:")
            for i, skill in enumerate(skills_data[:3]):
                print(f"   {i+1}. {skill.get('name_jp', 'Unknown')} (ID: {skill.get('id', 'N/A')})")
                print(f"      Description: {skill.get('description_en', 'N/A')[:60]}...")

    else:
        print("❌ No skills data was extracted")

if __name__ == "__main__":
    main()
