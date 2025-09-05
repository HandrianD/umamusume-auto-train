import re
import json
import glob
import os
from datetime import datetime
from typing import Dict, Any, Optional

from utils.screenshot import capture_region, enhanced_screenshot
from core.ocr import extract_text, extract_number
from core.recognizer import match_template

from utils.constants import SUPPORT_CARD_ICON_REGION, MOOD_REGION, TURN_REGION, FAILURE_REGION, YEAR_REGION, MOOD_LIST, CRITERIA_REGION, SKILL_PTS_REGION, ENERGY_REGION, ENERGY_LIST

is_bot_running = False

MINIMUM_MOOD = None
PRIORITIZE_G1_RACE = None
IS_AUTO_BUY_SKILL = None
SKILL_PTS_CHECK = None
PRIORITY_STAT = None
PRIORITY_WEIGHT = None
PRIORITY_WEIGHTS = None
PRIORITY_EFFECTS_LIST = None
MAX_FAILURE = None
STAT_CAPS = None
SKILL_LIST = None
CANCEL_CONSECUTIVE_RACE = None
CHARACTER_DATA = None
SUPPORT_CARDS_DATA = None
SCENARIO_DATA = None
EVENT_DATA_COLLECTION = None
USER_INTERVENTION_TIMEOUT = None

# Energy Management Configuration
NEVER_REST_ENERGY = None
SKIP_TRAINING_ENERGY = None
SKIP_INFIRMARY_UNLESS_MISSING_ENERGY = None
ENERGY_DETECTION_ENABLED = None

def load_config():
  with open("config.json", "r", encoding="utf-8") as file:
    return json.load(file)

def reload_config():
  global PRIORITY_STAT, MINIMUM_MOOD, MAX_FAILURE, PRIORITIZE_G1_RACE, CANCEL_CONSECUTIVE_RACE, STAT_CAPS, IS_AUTO_BUY_SKILL, SKILL_PTS_CHECK, SKILL_LIST, CHARACTER_DATA, SUPPORT_CARDS_DATA, SCENARIO_DATA, EVENT_DATA_COLLECTION, USER_INTERVENTION_TIMEOUT, NEVER_REST_ENERGY, SKIP_TRAINING_ENERGY, SKIP_INFIRMARY_UNLESS_MISSING_ENERGY, ENERGY_DETECTION_ENABLED, PRIORITY_WEIGHT, PRIORITY_WEIGHTS, PRIORITY_EFFECTS_LIST
  config = load_config()

  PRIORITY_STAT = config["priority_stat"]
  MINIMUM_MOOD = config["minimum_mood"]
  MAX_FAILURE = config["maximum_failure"]
  PRIORITIZE_G1_RACE = config["prioritize_g1_race"]
  CANCEL_CONSECUTIVE_RACE = config["cancel_consecutive_race"]
  STAT_CAPS = config["stat_caps"]
  IS_AUTO_BUY_SKILL = config["skill"]["is_auto_buy_skill"]
  SKILL_PTS_CHECK = config["skill"]["skill_pts_check"]
  SKILL_LIST = config["skill"]["skill_list"]

  # Load energy management settings
  energy_config = config.get("energy_management", {})
  ENERGY_DETECTION_ENABLED = energy_config.get("enabled", False)
  NEVER_REST_ENERGY = energy_config.get("never_rest_energy", 70)
  SKIP_TRAINING_ENERGY = energy_config.get("skip_training_energy", 30)
  SKIP_INFIRMARY_UNLESS_MISSING_ENERGY = energy_config.get("skip_infirmary_unless_missing_energy", True)

  # Load event data collection settings
  EVENT_DATA_COLLECTION = config.get("event_data_collection", {
    "enabled": True,
    "event_types": {
      "character_events": True,
      "support_card_events": True,
      "scenario_events": True,
      "random_events": False,
      "special_events": True
    },
    "data_to_collect": {
      "stat_changes": True,
      "mood_changes": True,
      "skill_gains": True,
      "training_efficiency": False
    },
    "context_tracking": {
      "current_stats": True,
      "support_cards": True,
      "training_year": True
    },
    "learning_features": {
      "personal_learning": True,
      "smart_defaults": True,
      "minimum_importance_threshold": 3
    }
  })

  # Load user intervention timeout (default 10 seconds)
  event_data = config.get("event_data_collection", {})
  USER_INTERVENTION_TIMEOUT = event_data.get("user_intervention_timeout", 10)

  # Load priority weight settings
  PRIORITY_WEIGHT = config.get("priority_weight", "NONE")
  PRIORITY_WEIGHTS = config.get("priority_weights", [1.0, 1.0, 1.0, 1.0, 1.0])
  
  # Define priority effects list based on priority weight level
  if PRIORITY_WEIGHT == "HEAVY":
    PRIORITY_EFFECTS_LIST = [1.5, 1.2, 1.0, 0.7, 0.4]
  elif PRIORITY_WEIGHT == "MEDIUM":
    PRIORITY_EFFECTS_LIST = PRIORITY_WEIGHTS
  elif PRIORITY_WEIGHT == "LIGHT":
    PRIORITY_EFFECTS_LIST = [1.2, 1.1, 1.0, 0.9, 0.8]
  else:  # NONE
    PRIORITY_EFFECTS_LIST = [1.0, 1.0, 1.0, 1.0, 1.0]

  # Load character data
  CHARACTER_DATA = None
  if config.get("character") and config["character"] is not None:
    char_id = config["character"]["id"]
    char_name = config["character"]["name"]
    # Look for both {char_id}.json and {char_id}-*.json patterns in nested directory
    char_json_files = glob.glob(f"assets/character/nested/{char_id}.json") or glob.glob(f"assets/character/nested/{char_id}-*.json")
    if char_json_files:
      try:
        with open(char_json_files[0], 'r', encoding='utf-8') as f:
          nested_data = json.load(f)
          # Extract English events from nested structure (events with choices)
          events_data = nested_data.get("data", {}).get("english", {}).get("events", [])
          CHARACTER_DATA = {
            "id": char_id,
            "name": char_name,
            "events": events_data
          }
        print(f"[CONFIG] Loaded character data for: {char_name}")
      except Exception as e:
        print(f"[ERROR] Failed to load character data: {e}")
    else:
      # Try to scrape character data on-demand
      print(f"[CONFIG] Character data not found locally for: {char_name} (ID: {char_id})")
      print(f"[CONFIG] Attempting on-demand scraping...")
      try:
        from server.scraper_service import scrape_character_on_demand
        success = scrape_character_on_demand(char_id, "nested")
        if success:
          # Try to load again after scraping (check both patterns)
          char_json_files = glob.glob(f"assets/character/nested/{char_id}.json") or glob.glob(f"assets/character/nested/{char_id}-*.json")
          if char_json_files:
            with open(char_json_files[0], 'r', encoding='utf-8') as f:
              nested_data = json.load(f)
              # Extract English events from nested structure (events with choices)
              events_data = nested_data.get("data", {}).get("english", {}).get("events", [])
              CHARACTER_DATA = {
                "id": char_id,
                "name": char_name,
                "events": events_data
              }
            print(f"[CONFIG] Successfully scraped and loaded character data for: {char_name}")
          else:
            print(f"[ERROR] Scraping completed but character file not found for: {char_name}")
        else:
          print(f"[ERROR] Failed to scrape character data for: {char_name}")
      except Exception as e:
        print(f"[ERROR] On-demand scraping failed: {e}")

  # Load support cards data
  SUPPORT_CARDS_DATA = []
  if config.get("support_cards") and config["support_cards"] is not None:
    for i, card in enumerate(config["support_cards"]):
      if card is not None:
        card_id = card["id"]
        card_name = card["name"]
        # Look for both {card_id}.json and {card_id}-*.json patterns in nested directory
        card_json_files = glob.glob(f"assets/support/nested/{card_id}.json") or glob.glob(f"assets/support/nested/{card_id}-*.json")
        if card_json_files:
          try:
            with open(card_json_files[0], 'r', encoding='utf-8') as f:
              card_nested_data = json.load(f)
              # Extract the English events from the nested structure
              # Handle both old format (direct events array) and new format (categorized events)
              events_data = card_nested_data.get("data", {}).get("english", {}).get("events", [])
              
              card_events = []
              if events_data:
                # Check if this is the new format (categorized with events inside categories)
                if isinstance(events_data[0], dict) and "events" in events_data[0]:
                  # New format: extract events from categories
                  for category in events_data:
                    if "events" in category:
                      card_events.extend(category["events"])
                else:
                  # Old format: events are directly in the array
                  card_events = events_data
              
              card_data = {
                "id": card_id,
                "name": card_name,
                "events": card_events
              }
              SUPPORT_CARDS_DATA.append(card_data)
            print(f"[CONFIG] Loaded support card data for: {card_name} (Slot {i+1})")
          except Exception as e:
            print(f"[ERROR] Failed to load support card data for slot {i+1}: {e}")
            SUPPORT_CARDS_DATA.append(None)
        else:
          # Try alternative ID formats (gametora IDs vs in-game IDs)
          alt_card_json_files = glob.glob(f"assets/support/nested/*.json")
          found_alt = False
          for alt_file in alt_card_json_files:
            if card_name.lower().replace(" ", "-") in alt_file.lower():
              try:
                with open(alt_file, 'r', encoding='utf-8') as f:
                  card_nested_data = json.load(f)
                  # Extract the English events from the nested structure
                  # Handle both old format (direct events array) and new format (categorized events)
                  events_data = card_nested_data.get("data", {}).get("english", {}).get("events", [])
                  
                  card_events = []
                  if events_data:
                    # Check if this is the new format (categorized with events inside categories)
                    if isinstance(events_data[0], dict) and "events" in events_data[0]:
                      # New format: extract events from categories
                      for category in events_data:
                        if "events" in category:
                          card_events.extend(category["events"])
                    else:
                      # Old format: events are directly in the array
                      card_events = events_data
                  
                  card_data = {
                    "id": card_id,
                    "name": card_name,
                    "events": card_events
                  }
                  SUPPORT_CARDS_DATA.append(card_data)
                print(f"[CONFIG] Loaded support card data for: {card_name} (Slot {i+1}) via name match")
                found_alt = True
                break
              except Exception as e:
                print(f"[ERROR] Failed to load alternative support card data for slot {i+1}: {e}")
          
          if not found_alt:
            # Try on-demand scraping as final fallback
            print(f"[CONFIG] Support card data not found for: {card_name} (ID: {card_id})")
            print(f"[CONFIG] Attempting on-demand scraping...")
            try:
              from server.scraper_service import scrape_support_card_on_demand
              success = scrape_support_card_on_demand(card_id, "nested")
              if success:
                # Try to load again after scraping (check both patterns)
                card_json_files = glob.glob(f"assets/support/nested/{card_id}.json") or glob.glob(f"assets/support/nested/{card_id}-*.json")
                if card_json_files:
                  with open(card_json_files[0], 'r', encoding='utf-8') as f:
                    card_nested_data = json.load(f)
                    # Extract the English events from the nested structure
                    # Handle both old format (direct events array) and new format (categorized events)
                    events_data = card_nested_data.get("data", {}).get("english", {}).get("events", [])
                    
                    card_events = []
                    if events_data:
                      # Check if this is the new format (categorized with events inside categories)
                      if isinstance(events_data[0], dict) and "events" in events_data[0]:
                        # New format: extract events from categories
                        for category in events_data:
                          if "events" in category:
                            card_events.extend(category["events"])
                      else:
                        # Old format: events are directly in the array
                        card_events = events_data
                    
                    card_data = {
                      "id": card_id,
                      "name": card_name,
                      "events": card_events
                    }
                    SUPPORT_CARDS_DATA.append(card_data)
                  print(f"[CONFIG] Successfully scraped and loaded support card data for: {card_name} (Slot {i+1})")
                else:
                  print(f"[ERROR] Scraping completed but support card file not found for: {card_name}")
                  SUPPORT_CARDS_DATA.append(None)
              else:
                print(f"[ERROR] Failed to scrape support card data for: {card_name}")
                SUPPORT_CARDS_DATA.append(None)
            except Exception as e:
              print(f"[ERROR] On-demand scraping failed for support card: {e}")
              SUPPORT_CARDS_DATA.append(None)
      else:
        SUPPORT_CARDS_DATA.append(None)

  # Load scenario data
  SCENARIO_DATA = None
  if config.get("scenario") and config["scenario"] is not None:
    scenario_id = config["scenario"]["id"]
    scenario_name = config["scenario"]["name"]
    scenario_json_files = glob.glob(f"assets/scenario/{scenario_id}.json")
    if scenario_json_files:
      try:
        with open(scenario_json_files[0], 'r', encoding='utf-8') as f:
          SCENARIO_DATA = {
            "id": scenario_id,
            "name": scenario_name,
            "events": json.load(f)
          }
        print(f"[CONFIG] Loaded scenario data for: {scenario_name}")
      except Exception as e:
        print(f"[ERROR] Failed to load scenario data: {e}")

  print(f"[CONFIG] Loaded {len([c for c in SUPPORT_CARDS_DATA if c is not None])} support cards")
  print(f"[CONFIG] Character data loaded: {CHARACTER_DATA is not None}")
  print(f"[CONFIG] Support cards data loaded: {len([c for c in SUPPORT_CARDS_DATA if c is not None])} cards")
  print(f"[CONFIG] Scenario data loaded: {SCENARIO_DATA is not None}")
  print(f"[CONFIG] Total events available: {len(get_character_events()) + len(get_all_support_card_events()) + len(get_scenario_events_with_choices()) + len(get_scenario_events_without_choices())}")

# Get Stat
def stat_state():
  stat_regions = {
    "spd": (310, 723, 55, 20),
    "sta": (405, 723, 55, 20),
    "pwr": (500, 723, 55, 20),
    "guts": (595, 723, 55, 20),
    "wit": (690, 723, 55, 20)
  }

  result = {}
  for stat, region in stat_regions.items():
    img = enhanced_screenshot(region)
    val = extract_number(img)
    result[stat] = val
  return result

# Check support card in each training
def check_support_card(threshold=0.8):
  SUPPORT_ICONS = {
    "spd": "assets/icons/support_card_type_spd.png",
    "sta": "assets/icons/support_card_type_sta.png",
    "pwr": "assets/icons/support_card_type_pwr.png",
    "guts": "assets/icons/support_card_type_guts.png",
    "wit": "assets/icons/support_card_type_wit.png",
    "friend": "assets/icons/support_card_type_friend.png"
  }

  count_result = {}

  for key, icon_path in SUPPORT_ICONS.items():
    matches = match_template(icon_path, SUPPORT_CARD_ICON_REGION, threshold)
    count_result[key] = len(matches)

  return count_result

# Get failure chance (idk how to get energy value)
def check_failure():
  failure = enhanced_screenshot(FAILURE_REGION)
  failure_text = extract_text(failure).lower()

  if not failure_text.startswith("failure"):
    return -1

  # SAFE CHECK
  # 1. If there is a %, extract the number before the %
  match_percent = re.search(r"failure\s+(\d{1,3})%", failure_text)
  if match_percent:
    return int(match_percent.group(1))

  # 2. If there is no %, but there is a 9, extract digits before the 9
  match_number = re.search(r"failure\s+(\d+)", failure_text)
  if match_number:
    digits = match_number.group(1)
    idx = digits.find("9")
    if idx > 0:
      num = digits[:idx]
      return int(num) if num.isdigit() else -1
    elif digits.isdigit():
      return int(digits)  # fallback

  return -1

# Check mood
def check_mood():
  mood = capture_region(MOOD_REGION)
  mood_text = extract_text(mood).upper()

  for known_mood in MOOD_LIST:
    if known_mood in mood_text:
      return known_mood

  print(f"[WARNING] Mood not recognized: {mood_text}")
  return "UNKNOWN"

def check_energy():
  """
  Detect current energy level of the character
  Returns energy level as a string and numeric value (0-100)
  """
  if not ENERGY_DETECTION_ENABLED:
    return "UNKNOWN", 50  # Default to middle value if detection disabled
    
  try:
    energy_img = capture_region(ENERGY_REGION)
    energy_text = extract_text(energy_img).upper()
    
    # Try to extract numeric energy value first
    energy_number = extract_number(energy_img)
    if energy_number is not None and 0 <= energy_number <= 100:
      # Classify energy level based on numeric value
      if energy_number >= 80:
        energy_level = "FULL"
      elif energy_number >= 60:
        energy_level = "HIGH" 
      elif energy_number >= 40:
        energy_level = "NORMAL"
      elif energy_number >= 20:
        energy_level = "LOW"
      else:
        energy_level = "EMPTY"
      
      print(f"[ENERGY] Detected energy: {energy_level} ({energy_number}%)")
      return energy_level, energy_number
    
    # Fallback to text-based detection
    for known_energy in ENERGY_LIST:
      if known_energy in energy_text:
        # Convert text to approximate numeric value
        energy_numeric = {
          "FULL": 90, "HIGH": 70, "NORMAL": 50, "LOW": 30, "EMPTY": 10, "UNKNOWN": 50
        }.get(known_energy, 50)
        
        print(f"[ENERGY] Detected energy (text): {known_energy} (~{energy_numeric}%)")
        return known_energy, energy_numeric
    
    print(f"[WARNING] Energy not recognized: {energy_text}")
    return "UNKNOWN", 50
    
  except Exception as e:
    print(f"[ERROR] Failed to check energy: {e}")
    return "UNKNOWN", 50

def get_current_energy_level():
  """
  Get current energy level as numeric value (0-100)
  Convenience function for energy-based decisions
  """
  _, energy_value = check_energy()
  return energy_value

# Character and Support Card Event Functions

def get_character_events():
  """Get all events for the selected character"""
  if CHARACTER_DATA and "events" in CHARACTER_DATA:
    return CHARACTER_DATA["events"]
  return []

def get_support_card_events(card_index):
  """Get events for a specific support card by slot index"""
  if SUPPORT_CARDS_DATA and card_index < len(SUPPORT_CARDS_DATA):
    card_data = SUPPORT_CARDS_DATA[card_index]
    if card_data and "events" in card_data:
      return card_data["events"]
  return []

def get_all_support_card_events():
  """Get events for all selected support cards"""
  all_events = []
  if SUPPORT_CARDS_DATA:
    for i, card_data in enumerate(SUPPORT_CARDS_DATA):
      if card_data and "events" in card_data:
        all_events.extend(card_data["events"])
  return all_events

def get_scenario_events():
  """Get all events for the selected scenario"""
  if SCENARIO_DATA and "events" in SCENARIO_DATA:
    return SCENARIO_DATA["events"]
  return {}

def get_scenario_events_with_choices():
  """Get scenario events that have choices"""
  scenario_events = get_scenario_events()
  if "events_with_choices" in scenario_events:
    return scenario_events["events_with_choices"]
  return []

def get_scenario_events_without_choices():
  """Get scenario events that don't have choices"""
  scenario_events = get_scenario_events()
  if "events_without_choices" in scenario_events:
    return scenario_events["events_without_choices"]
  return []

def find_event_choice(event_name, event_type="character"):
  """
  Find the optimal choice for a given event
  event_type: "character", "support", or "scenario"
  """
  if event_type == "character":
    events = get_character_events()
  elif event_type == "scenario":
    # For scenario events, we need to search in both events_with_choices and events_without_choices
    scenario_events = get_scenario_events()
    all_scenario_events = []
    
    # Add events with choices
    if "events_with_choices" in scenario_events:
      all_scenario_events.extend(scenario_events["events_with_choices"])
    
    # Add events without choices (these don't have options)
    if "events_without_choices" in scenario_events:
      for event in scenario_events["events_without_choices"]:
        event_copy = event.copy()
        event_copy["options"] = []  # No choices available
        all_scenario_events.append(event_copy)
    
    events = all_scenario_events
  else:
    events = get_all_support_card_events()

  for event in events:
    if event_name.lower() in event.get("name", "").lower():
      # Handle different option structures
      if event_type == "scenario":
        # Scenario events use "choices" array with "option" and "effects"
        choices = event.get("choices", [])
        if choices:
          return [choice.get("option", "") for choice in choices]
        else:
          return []  # No choices available
      else:
        # Character/support events use "options" array
        return event.get("options", [])

  return []

# Event Detection and Handling Functions

def detect_event_text():
  """
  Use OCR to detect event text from the screen
  Returns the detected event text or None if no event detected
  """
  from core.ocr import extract_text
  from utils.constants import EVENT_TEXT_REGION

  try:
    # Capture event text region
    event_img = enhanced_screenshot(EVENT_TEXT_REGION)
    event_text = extract_text(event_img)

    if event_text and len(event_text.strip()) > 10:  # Minimum length to be considered valid event text
      # Clean the text
      clean_text = event_text.strip()

      # Filter out OCR garbage (text with too many non-alphanumeric characters)
      alphanumeric_ratio = sum(c.isalnum() or c.isspace() for c in clean_text) / len(clean_text)
      if alphanumeric_ratio < 0.6:
        print(f"[EVENT] Detected text appears to be OCR garbage (low alphanumeric ratio): '{clean_text}'")
        return None

      # Filter out very short words or fragments
      words = clean_text.split()
      if len(words) < 2:
        print(f"[EVENT] Detected text too short/fragmented: '{clean_text}'")
        return None

      # Filter out common UI text that might be misread as events
      ui_keywords = [
        'year', 'late', 'nov', 'place', 'top', 'asz', 'calendar', 'schedule', 'race',
        'turn', 'next', 'debut', 'junior', 'goal', 'achieved', 'clear', 'g1', 'g2', 'g3',
        'place top', 'let\'s do it', 'make debut', 'next g1', 'goals achieved',
        'this was a victory', 'victory', 'as the empress', 'my wish is to',
        'always strive', 'standard', 'performance', 'result', 'outcome',
        'congratulations', 'well done', 'defeat', 'win', 'lose'
      ]
      lower_text = clean_text.lower()

      # Check if this looks like UI text rather than event text
      if any(keyword in lower_text for keyword in ui_keywords):
        print(f"[EVENT] Detected text appears to be UI text, not event: '{clean_text}'")
        return None

      # Additional check: reject text that looks like post-race dialogue
      post_race_keywords = [
        'this was a victory', 'victory', 'as the empress', 'my wish is to',
        'always strive', 'standard', 'performance', 'result', 'outcome'
      ]
      if any(keyword in lower_text for keyword in post_race_keywords):
        print(f"[EVENT] Detected text appears to be post-race dialogue, not event: '{clean_text}'")
        return None

      # Check for event-specific indicators
      event_indicators = [
        'trainer', 'support', 'scenario', 'event', 'choice', 'decision',
        'training', 'practice', 'lesson', 'skill', 'ability', 'stats'
      ]

      has_event_indicator = any(indicator in lower_text for indicator in event_indicators)
      if not has_event_indicator:
        print(f"[EVENT] No event indicators found in text: '{clean_text}'")
        return None

      print(f"[EVENT] Detected event text: '{clean_text}'")
      return clean_text

  except Exception as e:
    print(f"[ERROR] Failed to detect event text: {e}")

  return None

def detect_event_choices():
  """
  Use OCR to detect all event choices from the large choice area
  Returns a list of choice texts or empty list if none detected
  """
  from core.ocr import extract_text
  from utils.constants import CHOICE_AREA_REGION
  import re

  try:
    # Capture the entire choice area
    choice_img = enhanced_screenshot(CHOICE_AREA_REGION)
    choice_text = extract_text(choice_img)

    if not choice_text:
      return []

    print(f"[EVENT] Raw choice text detected: '{choice_text}'")

    # Parse choices using regex patterns
    choices = []

    # Look for patterns like "(choice 1 ...)", "(choice 2 ...)", etc.
    # Also handle variations like "1. ...", "Choice 1:", etc.
    patterns = [
      r'\(choice\s*1[^)]*\)(.*?)(?=\(choice\s*2|$)',  # (choice 1 ...) until (choice 2
      r'\(choice\s*2[^)]*\)(.*?)(?=\(choice\s*3|$)',  # (choice 2 ...) until (choice 3
      r'\(choice\s*3[^)]*\)(.*?)(?=\(choice\s*4|$)',  # (choice 3 ...) until (choice 4
      r'\(choice\s*4[^)]*\)(.*)',                      # (choice 4 ...) until end
      r'1\.?\s*(.*?)(?=2\.|$)',                       # 1. ... until 2.
      r'2\.?\s*(.*?)(?=3\.|$)',                       # 2. ... until 3.
      r'3\.?\s*(.*?)(?=4\.|$)',                       # 3. ... until 4.
      r'4\.?\s*(.*)',                                 # 4. ... until end
    ]

    for pattern in patterns:
      matches = re.findall(pattern, choice_text, re.IGNORECASE | re.DOTALL)
      for match in matches:
        choice = match.strip()
        if choice and len(choice) > 3:  # Filter out very short matches
          choices.append(choice)

    # Remove duplicates and clean up
    unique_choices = []
    for choice in choices:
      if choice not in unique_choices:
        unique_choices.append(choice)

    if unique_choices:
      print(f"[EVENT] Detected {len(unique_choices)} choices: {unique_choices}")

    return unique_choices

  except Exception as e:
    print(f"[ERROR] Failed to detect event choices: {e}")
    return []

def find_best_event_match(event_text):
  """
  Find the best matching event from character and support card data
  Returns (event_type, event_data, confidence_score) or (None, None, 0)
  """
  if not event_text:
    return None, None, 0

  best_match = None
  best_score = 0
  best_type = None

  # Search character events
  if CHARACTER_DATA and "events" in CHARACTER_DATA:
    char_events_data = CHARACTER_DATA["events"]
    # Handle both old format (with english_events) and new nested format (direct events list)
    if isinstance(char_events_data, list):
      # New nested format: events is directly a list
      for event in char_events_data:
        if isinstance(event, dict) and "name" in event:
          score = calculate_text_similarity(event_text, event["name"])
          if score > best_score:
            best_score = score
            best_match = event
            best_type = "character"
            print(f"[EVENT] Character event match: '{event['name']}' -> score: {score:.2f}")
    elif isinstance(char_events_data, dict) and "english_events" in char_events_data:
      # Old format: events contains english_events
      for event in char_events_data["english_events"]:
        if isinstance(event, dict) and "name" in event:
          score = calculate_text_similarity(event_text, event["name"])
          if score > best_score:
            best_score = score
            best_match = event
            best_type = "character"
            print(f"[EVENT] Character event match: '{event['name']}' -> score: {score:.2f}")

  # Search support card events
  if SUPPORT_CARDS_DATA:
    for card_data in SUPPORT_CARDS_DATA:
      if card_data and "events" in card_data:
        # Handle nested support card structure with categories
        if isinstance(card_data["events"], list):
          # New nested format: events contains categories
          for category in card_data["events"]:
            if isinstance(category, dict) and "events" in category:
              for event in category["events"]:
                if isinstance(event, dict) and "name" in event:
                  score = calculate_text_similarity(event_text, event["name"])
                  if score > best_score:
                    best_score = score
                    best_match = event
                    best_type = "support"
                    print(f"[EVENT] Support event match: '{event['name']}' -> score: {score:.2f}")
        else:
          # Old format: events is directly a list or dict
          for event in card_data["events"]:
            if isinstance(event, dict) and "name" in event:
              score = calculate_text_similarity(event_text, event["name"])
              if score > best_score:
                best_score = score
                best_match = event
                best_type = "support"
                print(f"[EVENT] Support event match: '{event['name']}' -> score: {score:.2f}")

  # Search scenario events
  if SCENARIO_DATA and "events" in SCENARIO_DATA:
    scenario_events_data = SCENARIO_DATA["events"]
    
    # Search events with choices
    if "events_with_choices" in scenario_events_data:
      for event in scenario_events_data["events_with_choices"]:
        if isinstance(event, dict) and "name" in event:
          score = calculate_text_similarity(event_text, event["name"])
          if score > best_score:
            best_score = score
            best_match = event
            best_type = "scenario"
            print(f"[EVENT] Scenario event match: '{event['name']}' -> score: {score:.2f}")
    
    # Search events without choices
    if "events_without_choices" in scenario_events_data:
      for event in scenario_events_data["events_without_choices"]:
        if isinstance(event, dict) and "name" in event:
          score = calculate_text_similarity(event_text, event["name"])
          if score > best_score:
            best_score = score
            best_match = event
            best_type = "scenario"
            print(f"[EVENT] Scenario event match: '{event['name']}' -> score: {score:.2f}")

  print(f"[EVENT] Best match score: {best_score:.2f} for type: {best_type}")

  if best_score > 0.2:  # Lowered threshold for better matching with OCR text
    print(f"[EVENT] Best match: '{best_match}' (confidence: {best_score:.2f})")
    return best_type, best_match, best_score

  # If no good match found, try fuzzy matching with common event keywords
  print(f"[EVENT] No good match found, trying fuzzy keyword matching...")
  fuzzy_result = find_fuzzy_event_match(event_text)
  if fuzzy_result[0] is not None:
    return fuzzy_result
  
  # If still no match found, return a default tuple
  print(f"[EVENT] No match found for event text: '{event_text}'")
  return None, None, 0

def find_fuzzy_event_match(event_text):
  """
  Try to find an event match using fuzzy keyword matching
  This is used when direct text matching fails
  """
  if not event_text:
    return None, None, 0

  # Check for Victory events first (special handling)
  lower_text = event_text.lower()
  if any(victory_keyword in lower_text for victory_keyword in ['victor', 'victory', 'win', 'won']):
    print(f"[EVENT] Victory event detected: '{event_text}' - using choice 1 (Top Option)")
    return "victory", {"type": "victory", "auto_choice": 1}, 0.9

  # Common event keywords that might appear in OCR text
  event_keywords = {
    'training': ['train', 'practice', 'lesson', 'study', 'learn'],
    'race': ['race', 'compete', 'competition', 'match'],
    'friendship': ['friend', 'relationship', 'bond', 'together'],
    'skill': ['skill', 'technique', 'ability', 'talent'],
    'rest': ['rest', 'relax', 'break', 'holiday'],
    'date': ['date', 'outing', 'walk', 'meal'],
    'fan': ['fan', 'supporter', 'cheer', 'support']
  }

  matched_categories = []

  # Check which categories the OCR text might match
  for category, keywords in event_keywords.items():
    if any(keyword in lower_text for keyword in keywords):
      matched_categories.append(category)

  if matched_categories:
    print(f"[EVENT] Fuzzy match found categories: {matched_categories}")

    # For now, return a generic match that will use choice analysis
    # In the future, this could be improved to match specific events
    return "fuzzy", {"type": "generic", "categories": matched_categories}, 0.1

  # If no keywords matched, return a default tuple instead of None
  print(f"[EVENT] No fuzzy keyword matches found for: '{event_text}'")
  return None, None, 0

  best_match = None
  best_score = 0
  best_type = None

  # Search character events
  if CHARACTER_DATA and "events" in CHARACTER_DATA:
    for category in CHARACTER_DATA["events"]:
      for event in category.get("events", []):
        if isinstance(event, str):
          # Simple string matching for character events
          score = calculate_text_similarity(event_text, event)
          if score > best_score:
            best_score = score
            best_match = event
            best_type = "character"
            print(f"[EVENT] Character event match: '{event}' -> score: {score:.2f}")

  # Search support card events
  if SUPPORT_CARDS_DATA:
    for card_data in SUPPORT_CARDS_DATA:
      if card_data and "events" in card_data:
        for category in card_data["events"]:
          for event in category.get("events", []):
            if isinstance(event, dict) and "name" in event:
              score = calculate_text_similarity(event_text, event["name"])
              if score > best_score:
                best_score = score
                best_match = event
                best_type = "support"
                print(f"[EVENT] Support event match: '{event['name']}' -> score: {score:.2f}")

  print(f"[EVENT] Best match score: {best_score:.2f} for type: {best_type}")

  if best_score > 0.2:  # Lowered threshold for better matching with OCR text
    print(f"[EVENT] Best match: '{best_match}' (confidence: {best_score:.2f})")
    return best_type, best_match, best_score

  # If no good match found, try fuzzy matching with common event keywords
  print(f"[EVENT] No good match found, trying fuzzy keyword matching...")
  fuzzy_result = find_fuzzy_event_match(event_text)
  if fuzzy_result[0] is not None:
    return fuzzy_result
  
  # If still no match found, return a default tuple
  print(f"[EVENT] No match found for event text: '{event_text}'")
  return None, None, 0

def calculate_text_similarity(text1, text2):
  """
  Calculate similarity between two text strings
  Now includes Japanese to English translation matching
  Returns a score between 0 and 1
  """
  if not text1 or not text2:
    return 0

  # Convert both texts to lowercase for comparison
  text1_lower = text1.lower()
  text2_lower = text2.lower()

  # Try direct matching first
  words1 = set(text1_lower.split())
  words2 = set(text2_lower.split())

  if not words1 or not words2:
    return 0

  intersection = words1.intersection(words2)
  union = words1.union(words2)

  # Calculate Jaccard similarity
  direct_similarity = len(intersection) / len(union)

  # If direct similarity is good enough, return it
  if direct_similarity > 0.3:
    return direct_similarity

  # Try translation matching for Japanese events
  translated_similarity = calculate_translated_similarity(text1_lower, text2_lower)
  if translated_similarity > direct_similarity:
    print(f"[EVENT] Using translation match: {translated_similarity:.2f} vs direct: {direct_similarity:.2f}")
    return translated_similarity

  return direct_similarity

def calculate_translated_similarity(text1, text2):
  """
  Calculate similarity using Japanese to English translation mappings
  Returns a similarity score between 0 and 1
  """
  # Common Japanese to English translations for Uma Musume events
  translation_map = {
    # Training and practice
    'トレーニング': ['training', 'practice', 'lesson'],
    '自主トレ': ['self training', 'personal training'],
    '練習': ['practice', 'drill'],
    'レッスン': ['lesson', 'class'],
    'ダンス': ['dance', 'dancing'],
    '料理': ['cooking', 'cook', 'meal'],
    'ドライブ': ['drive', 'driving'],
    'スーパーカー': ['supercar', 'sports car'],

    # Social and friendship
    '友達': ['friend', 'friends'],
    '友情': ['friendship', 'bond'],
    '一緒に': ['together', 'with'],
    'お出かけ': ['outing', 'date'],
    '遊び': ['play', 'fun', 'hang out'],
    'カノジョ': ['girlfriend'],
    'ヘイ': ['hey'],

    # Food and meals
    'ご飯': ['meal', 'food', 'dinner'],
    '料理': ['cooking', 'cook'],
    '食べ物': ['food', 'eat'],
    'レストラン': ['restaurant'],
    'フィーバー': ['fever', 'excited'],

    # Competition and racing
    'レース': ['race', 'racing'],
    '競争': ['competition', 'contest'],
    '勝つ': ['win', 'victory'],
    '優勝': ['champion', 'first place'],

    # Emotions and feelings
    '楽しい': ['fun', 'enjoyable'],
    '嬉しい': ['happy', 'glad'],
    '悲しい': ['sad'],
    '疲れた': ['tired'],
    'ゾッコン': ['crazy about', 'obsessed'],

    # Common event words
    'イベント': ['event'],
    'ミッション': ['mission'],
    'クエスト': ['quest'],
    'チャンス': ['chance'],
    '機会': ['opportunity'],
    '思い出': ['memories', 'memory'],
    '味': ['taste', 'flavor']
  }

  # Check if text1 contains Japanese words that translate to text2
  score1 = get_translation_score(text1, text2, translation_map)

  # Check if text2 contains Japanese words that translate to text1
  score2 = get_translation_score(text2, text1, translation_map)

  return max(score1, score2)

def get_translation_score(text_with_japanese, text_with_english, translation_map):
  """
  Calculate similarity score by translating Japanese words to English
  """
  score = 0
  english_words = set(text_with_english.lower().split())

  for japanese_word, english_translations in translation_map.items():
    if japanese_word in text_with_japanese:
      # Check if any of the English translations appear in the English text
      for translation in english_translations:
        if translation.lower() in text_with_english.lower():
          score += 0.2  # Give points for each translation match
          break

  return min(score, 1.0)  # Cap at 1.0

def get_optimal_event_choice(event_data, event_type):
  """
  Get the optimal choice for a matched event
  Now uses database choice data for smarter decisions
  Returns the choice index (1-based) or 1 if no preference found
  """
  # First, try to get choices from database instead of OCR
  if event_data and isinstance(event_data, dict):
    event_text = event_data.get("name", "")
    if event_text:
      choices = get_event_choices_from_database(event_text, event_type)
      if choices:
        print(f"[EVENT] Analyzing {len(choices)} database choices for optimal decision")

        # Analyze choice content for keywords
        best_choice, _ = analyze_choice_content(choices)

        if best_choice > 0:
          print(f"[EVENT] Content analysis recommends choice {best_choice}")
          return best_choice, False  # False indicates not from database

  # Fallback to original logic
  if event_type == "character":
    # For character events, we might not have choice data yet
    return 1, False

  elif event_type == "support" and isinstance(event_data, dict):
    # Support card events might have choice preferences
    options = event_data.get("options", [])
    if options:
      return 1, False

  elif event_type == "scenario" and isinstance(event_data, dict):
    # Scenario events have different structures
    choices = event_data.get("choices", [])
    if choices:
      # Scenario events have choices with option and effects
      return 1, False  # Default to first choice for now
    else:
      # No choices available for this scenario event
      return 1, False

  elif event_type == "unknown":
    # For unknown events, we'll use choice content analysis
    return 1, False  # Default, but will be overridden by choice analysis

  return 1, False  # Default to first choice

def get_event_choices_from_database(event_text, event_type, return_full_data=False):
  """
  Get event choices from JSON database OR learned events
  Returns list of choice texts or empty list if not found
  Priority: Learned Events → Static Database → Not Found
  
  Args:
    event_text: The event text to search for
    event_type: The type of event (character, support, scenario)
    return_full_data: If True, returns full event data instead of just choices
  """
  try:
    # STEP 1: Check learned events first (from event_data.json)
    learned_choices = get_choices_from_learned_events(event_text)
    if learned_choices:
      print(f"[EVENT] ✅ Found event in LEARNED data: {len(learned_choices)} choices")
      if return_full_data:
        # Try to find the full learned event data
        try:
          data = _load_event_data_from_json()
          events = data.get("events", [])
          for event in events:
            if calculate_text_similarity(event.get('event_text', ''), event_text) > 0.8:
              return event
        except Exception as e:
          print(f"[DEBUG] Error loading learned event data: {e}")
        return None
      return learned_choices

    # STEP 2: Check static database (assets/character/, assets/support/, etc.)
    event_type_found, event_data, confidence = find_best_event_match(event_text)

    if event_data and confidence > 0.1:
      print(f"[EVENT] Found event in static database: '{event_data.get('name', 'Unknown')}' (confidence: {confidence:.2f})")

      if return_full_data:
        return event_data

      # Extract choices based on event type
      if event_type_found == "character":
        # Character events use "choices" array
        choices = event_data.get("choices", [])
        if choices:
          choice_texts = []
          for choice in choices:
            if isinstance(choice, dict):
              # Get the option text
              option_text = choice.get("option", "")
              if option_text:
                choice_texts.append(option_text)
          return choice_texts

      elif event_type_found == "support":
        # Support card events can use "options" array or "effects" array (nested format)
        options = event_data.get("options", [])
        effects = event_data.get("effects", [])
        
        if options:
          # Old format with options
          choice_texts = []
          for option in options:
            if isinstance(option, dict):
              option_text = option.get("option", option.get("text", ""))
              if option_text:
                choice_texts.append(option_text)
          return choice_texts
        elif effects:
          # New nested format with effects - extract choice options from strings
          choice_texts = []
          for effect in effects:
            if isinstance(effect, str):
              # Parse effect strings like "Top Option: Energy -10 Speed +15"
              if ":" in effect:
                choice_part = effect.split(":", 1)[0].strip()
                choice_texts.append(choice_part)
              else:
                choice_texts.append(f"Choice {len(choice_texts) + 1}")
          return choice_texts

      elif event_type_found == "scenario":
        # Scenario events use "choices" array
        choices = event_data.get("choices", [])
        if choices:
          choice_texts = []
          for choice in choices:
            if isinstance(choice, dict):
              option_text = choice.get("option", "")
              if option_text:
                choice_texts.append(option_text)
          return choice_texts

    print(f"[EVENT] Event not found in learned data OR static database")
    return []

  except Exception as e:
    print(f"[ERROR] Failed to get choices from database: {e}")
    return []

def get_choices_from_learned_events(event_text):
  """
  Check if this event was learned from user choices in event_data.json
  Returns list of choice texts if found, empty list if not found
  """
  try:
    data = _load_event_data_from_json()
    events = data.get("events", [])
    
    if not events:
      return []
    
    # Look for events with similar text that have user choices
    for event in events:
      stored_event_text = event.get('event_text', '')
      if stored_event_text and _events_are_similar(event_text, stored_event_text):
        # Check if this event has detected choices (preferred)
        detected_choices = event.get('detected_choices', [])
        if detected_choices and len(detected_choices) > 1:
          print(f"[EVENT] 🎓 Found learned event: '{stored_event_text}' with {len(detected_choices)} choices")
          return detected_choices
        
        # Even if no detected_choices, we know the user made a choice
        choice_made = event.get('choice_made')
        if choice_made:
          print(f"[EVENT] 🎓 Found learned event: '{stored_event_text}' (user previously chose {choice_made})")
          # Return dummy choices based on the choice number (we know this choice exists)
          try:
            max_choice = int(choice_made) if isinstance(choice_made, (str, int)) else 2
            # Ensure we have at least 2 choices if user made a choice
            max_choice = max(max_choice, 2)
            return [f"Choice {i+1}" for i in range(max_choice)]
          except:
            # Fallback: assume 2 choices if we can't parse choice_made
            return ["Choice 1", "Choice 2"]
    
    return []
    
  except Exception as e:
    print(f"[ERROR] Failed to check learned events: {e}")
    return []

def get_learned_choice_for_event(event_text):
  """
  Get the learned choice for a specific event if it exists
  Returns the choice number (1-5) if found, None otherwise
  """
  try:
    data = _load_event_data_from_json()
    events = data.get("events", [])
    
    if not events:
      return None
    
    # Look for events with similar text that have user choices
    for event in events:
      stored_event_text = event.get('event_text', '')
      if calculate_text_similarity(event_text, stored_event_text) > 0.6:  # Lowered from 0.8
        choice_made = event.get('choice_made')
        if choice_made:
          print(f"[EVENT] 🎓 Found learned choice: '{stored_event_text}' -> choice {choice_made}")
          return int(choice_made)
    
    return None
    
  except Exception as e:
    print(f"[ERROR] Failed to get learned choice: {e}")
    return None

def analyze_choice_content(choices):
  """
  Analyze choice text content to make intelligent decisions
  Now works with database choices instead of OCR text
  Returns the recommended choice index (1-based) or 0 if no preference
  """
  if not choices:
    return 0, False

  print(f"[EVENT] Analyzing choice content: {choices}")

  # Define keyword preferences (can be customized)
  # Skill hints get highest priority
  skill_keywords = [
    "hint", "skill", "technique", "ability", "talent",
    "burst", "red shift", "concentration", "professor", "maestro"
  ]

  positive_keywords = [
    "training", "practice", "improve", "learn", "study",
    "encourage", "support", "help", "assist", "guide",
    "focus", "concentrate", "dedicate", "commit"
  ]

  negative_keywords = [
    "rest", "relax", "skip", "avoid", "ignore",
    "quit", "give up", "stop", "leave", "abandon"
  ]

  choice_scores = []

  for i, choice_text in enumerate(choices):
    score = 0
    lower_text = choice_text.lower()

    # Skill hints get highest priority (+3 points each)
    for keyword in skill_keywords:
      if keyword in lower_text:
        score += 3
        print(f"[EVENT] Skill hint detected in choice {i+1}: '{keyword}'")

    # Count positive keywords (+1 point each)
    for keyword in positive_keywords:
      if keyword in lower_text:
        score += 1

    # Subtract negative keywords (-1 point each)
    for keyword in negative_keywords:
      if keyword in lower_text:
        score -= 1

    choice_scores.append((i + 1, score))  # (choice_index, score)

  # Sort by score (highest first)
  choice_scores.sort(key=lambda x: x[1], reverse=True)

  # Log the scoring for debugging
  if choice_scores:
    print(f"[EVENT] Choice scores: {[(f'Choice {idx}', score) for idx, score in choice_scores]}")
    best_choice, best_score = choice_scores[0]
    if best_score > 0:
      print(f"[EVENT] Best choice: {best_choice} (score: {best_score})")

  # If no strong preference, use a more balanced approach
  if choice_scores and choice_scores[0][1] >= 0:
    # If we have any choices with non-negative scores, pick the best one
    return choice_scores[0][0], False

  # Last resort: analyze choice text for basic heuristics
  if choices:
    for i, choice_text in enumerate(choices):
      lower_text = choice_text.lower()
      # Prefer choices that mention training or improvement
      if any(word in lower_text for word in ['train', 'practice', 'learn', 'improve', 'focus']):
        return i + 1, False  # 1-based index

  return 1, False  # Default to first choice as absolute fallback

def _log_event_to_database(event_text, choice_made, character, support_cards,
                          pre_stats, pre_mood, pre_year, event_type):
  """Log event to JSON file for learning"""
  try:
    import uuid
    from datetime import datetime

    # Get available choices from database instead of OCR
    detected_choices = get_event_choices_from_database(event_text, event_type)

    # Create session ID for tracking
    session_id = str(uuid.uuid4())[:8]

    # Event data structure
    event_data = {
      'session_id': session_id,
      'timestamp': datetime.now().isoformat(),
      'event_text': event_text,
      'detected_choices': detected_choices,  # Add detected choices from database
      'choice_made': choice_made,
      'character': character,
      'support_cards': support_cards,
      'current_stats': pre_stats,
      'current_mood': pre_mood,
      'current_year': pre_year,
      'event_type': event_type,
      'outcome': {}  # Will be updated after event completes
    }

    # Save to JSON file
    success = _save_event_to_json(event_data)
    if success:
      print(f"[EVENT] Logged event to JSON (session: {session_id})")
      if detected_choices:
        print(f"[EVENT] Recorded {len(detected_choices)} choices from database for analysis")
    else:
      print("[EVENT] Failed to log event to JSON")

  except Exception as e:
    print(f"[EVENT] Error logging to JSON: {e}")

def _save_event_to_json(event_data):
  """Save event data to JSON file"""
  try:
    json_file = "event_data.json"

    # Load existing data or create new structure
    if os.path.exists(json_file):
      with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    else:
      data = {
        "metadata": {
          "created": datetime.now().isoformat(),
          "total_events": 0,
          "version": "1.0"
        },
        "events": []
      }

    # Add new event
    data["events"].append(event_data)
    data["metadata"]["total_events"] = len(data["events"])
    data["metadata"]["last_updated"] = datetime.now().isoformat()

    # Save back to file
    with open(json_file, 'w', encoding='utf-8') as f:
      json.dump(data, f, indent=2, ensure_ascii=False)

    return True

  except Exception as e:
    print(f"[ERROR] Failed to save event to JSON: {e}")
    return False

def _parse_choice_effects(choices):
  """Parse choice effects into stat gains dictionary"""
  stat_gains = {}

  for i, choice in enumerate(choices):
    effects = []

    # Handle different choice formats
    if isinstance(choice, dict):
      if "effects" in choice:
        if isinstance(choice["effects"], list):
          effects = choice["effects"]  # Scenario format: ["Speed +10", "Power +5"]
        elif isinstance(choice["effects"], str):
          effects = [choice["effects"]]  # Character/Support format: "Speed +20"
      elif "option" in choice:
        # This is just the option text, effects might be elsewhere
        continue

    # Parse each effect string - handle complex formats like "Energy -10 Mood +1 Speed +10"
    for effect in effects:
      if isinstance(effect, str):
        # Split by spaces and process stat changes
        parts = effect.split()
        j = 0
        while j < len(parts) - 1:  # Need at least stat + value
          current_part = parts[j].lower()

          # Check if this is a stat name
          stat_mapping = {
            "speed": "spd",
            "stamina": "sta",
            "power": "pwr",
            "guts": "guts",
            "wisdom": "wit",
            "intelligence": "wit",
            "energy": "energy",
            "mood": "mood"
          }

          if current_part in stat_mapping:
            stat = stat_mapping[current_part]
            next_part = parts[j + 1]

            # Handle the value (could be +10, -10, etc.)
            if next_part.startswith(('+', '-')):
              try:
                # Extract just the number part
                value_str = ''.join(c for c in next_part if c.isdigit() or c in '+-')
                gain = int(value_str)
                stat_gains[f"choice_{i+1}_{stat}"] = gain
                j += 2  # Skip the value part
              except (ValueError, IndexError):
                j += 1
            else:
              j += 1
          else:
            j += 1

  return stat_gains

def _parse_choice_effects_support(options):
  """Parse support card choice effects into stat gains dictionary"""
  stat_gains = {}

  for i, option in enumerate(options):
    effects = []

    # Support card options have "effects" as a list of strings
    if isinstance(option, dict) and "effects" in option:
      if isinstance(option["effects"], list):
        effects = option["effects"]
      elif isinstance(option["effects"], str):
        effects = [option["effects"]]

    # Parse each effect string - handle complex formats like "Energy -10 Mood +1 Speed +10"
    for effect in effects:
      if isinstance(effect, str):
        # Split by spaces and process stat changes
        parts = effect.split()
        j = 0
        while j < len(parts) - 1:  # Need at least stat + value
          current_part = parts[j].lower()

          # Check if this is a stat name
          stat_mapping = {
            "speed": "spd",
            "stamina": "sta",
            "power": "pwr",
            "guts": "guts",
            "wisdom": "wit",
            "intelligence": "wit",
            "energy": "energy",
            "mood": "mood"
          }

          if current_part in stat_mapping:
            stat = stat_mapping[current_part]
            next_part = parts[j + 1]

            # Handle the value (could be +10, -10, etc.)
            if next_part.startswith(('+', '-')):
              try:
                # Extract just the number part
                value_str = ''.join(c for c in next_part if c.isdigit() or c in '+-')
                gain = int(value_str)
                stat_gains[f"choice_{i+1}_{stat}"] = gain
                j += 2  # Skip the value part
              except (ValueError, IndexError):
                j += 1
            else:
              j += 1
          else:
            j += 1

  return stat_gains

def _load_event_data_from_json():
  """Load event data from combined character, support card, and scenario directories"""
  try:
    # Load config to get character, support cards, and scenario
    config = load_config()
    character_id = config["character"]["id"]
    character_name = config["character"]["name"]
    support_cards = config["support_cards"]
    scenario_id = config["scenario"]["id"]

    all_events = []

    # Load character events - file name format: ID-slug.json
    character_slug = character_name.lower().replace(" ", "-")
    character_file = f"assets/character/combined/{character_id}-{character_slug}.json"
    if os.path.exists(character_file):
      with open(character_file, 'r', encoding='utf-8') as f:
        char_data = json.load(f)
        for event in char_data.get("english_events", []):
          if event.get("type") == "with_choices":
            # Convert to the format expected by the intelligence system
            event_entry = {
              "event_text": event["name"],
              "choice_made": 1,  # Default, will be overridden by analysis
              "outcome": {
                "stat_gains": _parse_choice_effects(event["choices"])
              }
            }
            all_events.append(event_entry)

    # Load support card events - find files by name matching
    for support_card in support_cards:
      support_name = support_card["name"]
      support_file = None

      # Try to find the correct file by name in nested directory
      if os.path.exists("assets/support/nested"):
        for filename in os.listdir("assets/support/nested"):
          if filename.endswith(".json"):
            # Check if the support card name (with spaces replaced by hyphens) is in the filename
            name_slug = support_name.lower().replace(" ", "-")
            if name_slug in filename.lower():
              support_file = f"assets/support/nested/{filename}"
              break

      if support_file and os.path.exists(support_file):
        with open(support_file, 'r', encoding='utf-8') as f:
          support_nested_data = json.load(f)
          
          # Extract events from nested structure - use english events with new format
          # Handle both old "combined" format and new "english" format
          support_events_data = support_nested_data.get("data", {}).get("english", {}).get("events", [])
          
          if not support_events_data:
            # Fallback to old "combined" format
            support_data = support_nested_data.get("data", {}).get("combined", support_nested_data)
            support_events_data = support_data.get("events", [])
          
          # Handle both new format (categorized events) and old format
          if support_events_data:
            for category_or_event in support_events_data:
              events_to_process = []
              
              # Check if this is new format (categories with events inside)
              if isinstance(category_or_event, dict) and "events" in category_or_event:
                # New format: extract events from category
                events_to_process = category_or_event["events"]
              elif isinstance(category_or_event, dict) and "name" in category_or_event:
                # Old format: this is directly an event
                events_to_process = [category_or_event]
              
              for event in events_to_process:
                # Handle multiple data formats:
                # 1. New format: "choices" array with {option, effects}
                # 2. Old format 1: "options" array with {effects}
                # 3. Old format 2: direct "effects" array
                
                choices = event.get("choices", [])
                options = event.get("options", [])
                direct_effects = event.get("effects", [])
                
                # Determine which format we're dealing with
                if choices and len(choices) > 1:
                  # New format with choices
                  event_entry = {
                    "event_text": event["name"],
                    "choice_made": 1,  # Default, will be overridden by analysis
                    "outcome": {
                      "stat_gains": _parse_choice_effects_support(choices)
                    }
                  }
                  all_events.append(event_entry)
                elif options and len(options) > 1:
                  # Old format with options
                  event_entry = {
                    "event_text": event["name"],
                    "choice_made": 1,  # Default, will be overridden by analysis
                    "outcome": {
                      "stat_gains": _parse_choice_effects_support(options)
                    }
                  }
                  all_events.append(event_entry)
                # Skip events with only direct effects (no choices)

    # Load scenario events - file name format: scenario-id.json
    scenario_file = f"assets/scenario/{scenario_id}.json"
    if os.path.exists(scenario_file):
      with open(scenario_file, 'r', encoding='utf-8') as f:
        scenario_data = json.load(f)
        for event in scenario_data.get("events_with_choices", []):
          # Convert to the format expected by the intelligence system
          event_entry = {
            "event_text": event["name"],
            "choice_made": 1,  # Default, will be overridden by analysis
            "outcome": {
              "stat_gains": _parse_choice_effects(event["choices"])
            }
          }
          all_events.append(event_entry)

    return {
      "events": all_events,
      "metadata": {
        "total_events": len(all_events),
        "character_id": character_id,
        "character_name": character_name,
        "support_cards_count": len(support_cards),
        "scenario_id": scenario_id
      }
    }

  except Exception as e:
    print(f"[ERROR] Failed to load event data from combined directories: {e}")
    return {"events": [], "metadata": {"total_events": 0}}

def get_optimal_event_choice_from_database(event_text, event_type):
  """
  Get optimal choice using JSON data learning
  Falls back to basic logic if no data available
  Returns (choice_index, from_database) tuple
  """
  try:
    # Load event data from JSON
    data = _load_event_data_from_json()
    events = data.get("events", [])

    if not events:
      print("[EVENT] No event data available, using fallback logic")
      return get_optimal_event_choice(None, event_type), False

    # Find similar events
    similar_events = []
    for event in events:
      if _events_are_similar(event_text, event['event_text']):
        similar_events.append(event)

    if not similar_events:
      print("[EVENT] No similar events found, using fallback logic")
      return get_optimal_event_choice(None, event_type), False

    # Analyze choice success rates
    choice_stats = _analyze_choice_success_rates(similar_events)

    if not choice_stats:
      print("[EVENT] Insufficient data for analysis, using fallback logic")
      return get_optimal_event_choice(None, event_type), False

    # Find best choice based on average score instead of success rate
    best_choice = max(choice_stats.items(), key=lambda x: x[1]['avg_score'])

    choice_num = int(best_choice[0])
    stats = best_choice[1]

    # Use average score as confidence metric
    if stats['sample_size'] >= 1:  # Lower threshold since we have actual stat data
      print(f"[EVENT] Event data recommends choice {choice_num} "
            f"(avg score: {stats['avg_score']:.1f}, "
            f"samples: {stats['sample_size']})")
      return choice_num, True

    print("[EVENT] Insufficient event data, using fallback logic")

  except Exception as e:
    print(f"[EVENT] JSON data query error: {e}, using fallback logic")

  # Fallback to basic choice selection
  return get_optimal_event_choice(None, event_type), False

def _events_are_similar(event1, event2):
  """Check if two events are similar based on text matching"""
  import re

  # Clean and normalize text
  def clean_text(text):
    # Remove punctuation and extra whitespace
    text = re.sub(r'[^\w\s]', '', text.lower())
    # Split into words
    words = text.split()
    # Remove common stop words that don't help with matching
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'event', 'trainee'}
    return [word for word in words if word not in stop_words and len(word) > 2]

  words1 = set(clean_text(event1))
  words2 = set(clean_text(event2))

  if not words1 or not words2:
    return False

  # Calculate Jaccard similarity
  intersection = len(words1.intersection(words2))
  union = len(words1.union(words2))

  if union == 0:
    return False

  similarity = intersection / union

  # Also check for substring matching for short events
  if len(words1) <= 3 or len(words2) <= 3:
    # For short events, check if one is a substring of the other
    text1_clean = re.sub(r'[^\w\s]', '', event1.lower())
    text2_clean = re.sub(r'[^\w\s]', '', event2.lower())
    if text1_clean in text2_clean or text2_clean in text1_clean:
      return True

  return similarity > 0.2  # Lowered threshold to 20% for better matching

def _analyze_choice_success_rates(events):
  """Analyze success rates for different choices in similar events based on stat gains"""
  choice_stats = {}

  # Get priority stats from config
  config = load_config()
  priority_stats = config.get("priority_stat", ["spd", "sta", "pwr", "wit", "guts"])

  for event in events:
    stat_gains = event.get('outcome', {}).get('stat_gains', {})

    # Score each choice based on stat gains and priority
    choice_scores = {}
    for key, gain in stat_gains.items():
      if key.startswith("choice_"):
        choice_num = key.split("_")[1]  # Extract choice number
        stat = key.split("_")[2] if len(key.split("_")) > 2 else ""

        if choice_num not in choice_scores:
          choice_scores[choice_num] = 0

        # Weight the gain by stat priority
        if stat in priority_stats:
          priority_weight = len(priority_stats) - priority_stats.index(stat)  # Higher priority = higher weight
          choice_scores[choice_num] += gain * priority_weight
        else:
          choice_scores[choice_num] += gain  # Default weight for non-priority stats

    # Track all choices and their scores
    for choice_num, score in choice_scores.items():
      if choice_num not in choice_stats:
        choice_stats[choice_num] = {
          'total_events': 0,
          'successful_events': 0,
          'success_rate': 0.0,
          'avg_score': 0.0
        }

      choice_stats[choice_num]['total_events'] += 1
      choice_stats[choice_num]['successful_events'] += 1  # All choices are "successful" in terms of being available
      choice_stats[choice_num]['avg_score'] += score

  # Calculate success rates and average scores
  for choice, stats in choice_stats.items():
    if stats['total_events'] > 0:
      stats['success_rate'] = stats['successful_events'] / stats['total_events']
      stats['avg_score'] = stats['avg_score'] / stats['total_events']
      stats['sample_size'] = stats['total_events']

  return choice_stats

def update_event_outcome(session_id: str, post_stats: Dict[str, int] = None,
                        post_mood: str = None, skill_points_gained: float = 0,
                        training_efficiency: float = 1.0):
  """
  Update the JSON file with post-event outcomes for learning
  This should be called after an event completes
  """
  if not session_id:
    return

  try:
    # Load current event data
    data = _load_event_data_from_json()
    events = data.get("events", [])

    # Find the event by session_id
    event_index = None
    for i, event in enumerate(events):
      if event.get('session_id') == session_id:
        event_index = i
        break

    if event_index is None:
      print(f"[EVENT] Event with session_id {session_id} not found")
      return

    # Calculate stat gains (simplified - in reality we'd need pre-event stats)
    stat_gains = {}
    if post_stats:
      stat_gains = post_stats  # Placeholder - should calculate actual gains

    outcome_data = {
      'stat_gains': stat_gains,
      'mood_change': post_mood,
      'skill_points': skill_points_gained,
      'training_efficiency': training_efficiency,
      'timestamp': datetime.now().isoformat()
    }

    # Update the event with outcome data
    events[event_index]['outcome'] = outcome_data

    # Save back to JSON
    data["events"] = events
    _save_event_to_json(data)

    print(f"[EVENT] Updated outcome data for session {session_id}")

  except Exception as e:
    print(f"[EVENT] Failed to update outcome: {e}")

def _calculate_mood_gain_from_outcome(before_mood: str, after_mood: str) -> float:
  """Calculate mood improvement from outcome data"""
  mood_values = {'WORST': 0, 'BAD': 1, 'NORMAL': 2, 'GOOD': 3, 'GREAT': 4, 'EXCELLENT': 5}
  before_val = mood_values.get(before_mood, 2)
  after_val = mood_values.get(after_mood, 2)
  return after_val - before_val

def handle_event():
  """
  Main event handling function with JSON logging
  Detects event, finds best match, makes optimal choice, and logs outcome
  Returns True if event was handled, False otherwise
  """
  print("[EVENT] Starting intelligent event detection...")

  # Reload config to pick up any changes made through web interface
  reload_config()

  # Detect event text
  event_text = detect_event_text()
  if not event_text:
    print("[EVENT] No event text detected")
    return False

  print(f"[EVENT] Detected event text: '{event_text}'")

  # Capture pre-event state
  pre_event_stats = stat_state()
  pre_event_mood = check_mood()
  pre_event_year = check_current_year()

  # Get current support cards info
  support_cards_info = get_support_cards_info()
  current_support_cards = [card['name'] for card in support_cards_info if card['name']]

  # Find best match
  event_type, event_data, confidence = find_best_event_match(event_text)

  print(f"[EVENT] Character loaded: {CHARACTER_DATA.get('name') if CHARACTER_DATA else 'None'}")
  print(f"[EVENT] Support cards loaded: {len(SUPPORT_CARDS_DATA) if SUPPORT_CARDS_DATA else 0}")
  print(f"[EVENT] Scenario loaded: {SCENARIO_DATA.get('name') if SCENARIO_DATA else 'None'}")
  print(f"[EVENT] Event data available: {len(get_character_events()) + len(get_all_support_card_events()) + len(get_scenario_events_with_choices()) + len(get_scenario_events_without_choices())} events")

  if not event_type:
    print("[EVENT] No matching event found - waiting for user intervention to learn from choice")
    print("[EVENT] Bot will wait 20 seconds for you to manually select a choice")

    # Wait for user intervention to learn from their choice
    user_choice = wait_for_user_intervention(20)

    if user_choice == "user_intervened":
      print("[EVENT] User intervened - event will be recorded for future learning")
      # The event will be logged when the choice is detected
      return True  # Event handled by user

    print("[EVENT] No user intervention - proceeding with choice content analysis")

    # Even without event match, we can still make intelligent choices using database
    choice_result = get_optimal_event_choice_from_database(event_text, "unknown")
    if isinstance(choice_result, tuple):
      choice_index, _ = choice_result
    else:
      choice_index = choice_result

    print(f"[EVENT] Making choice {choice_index} based on database choice content analysis")

    # Import here to avoid circular imports
    from core.execute import select_event_choice

    # Make the choice (pass event info for better choice count detection)
    success = select_event_choice(choice_index, event_text, "unknown")

    if success:
      print(f"[EVENT] Successfully selected choice {choice_index} using content analysis")
    else:
      print(f"[EVENT] Failed to select choice {choice_index}")

    return success

  # Get optimal choice using JSON learning
  choice_result = get_optimal_event_choice_from_database(event_text, event_type)
  if isinstance(choice_result, tuple):
    choice_index, from_database = choice_result
  else:
    # Handle backward compatibility
    choice_index = choice_result
    from_database = True

  # If choice is not from learned database data, wait for user intervention
  if not from_database:
    print("[EVENT] Choice based on fallback logic - waiting for user intervention to learn")
    print("[EVENT] Bot will wait 20 seconds for you to manually select a choice")

    # Wait for user intervention to learn from their choice
    user_choice = wait_for_user_intervention(20)

    if user_choice and isinstance(user_choice, int) and 1 <= user_choice <= 5:
      print(f"[EVENT] User manually selected choice {user_choice} - recording for future learning")
      
      # Log the user's choice for learning
      _log_user_choice_for_learning(event_text, user_choice, event_type, pre_event_stats, pre_event_mood, pre_event_year, current_support_cards)
      
      return True  # Event handled by user

    elif user_choice == "user_intervened":
      print("[EVENT] User intervened but choice detection failed - event will be recorded for future learning")
      # The event will be logged when the choice is detected
      return True  # Event handled by user

    print("[EVENT] No user intervention - proceeding with automatic choice")

  print(f"[EVENT] Making choice {choice_index} based on {'database learning' if from_database else 'fallback logic'}")

  # Import here to avoid circular imports
  from core.execute import select_event_choice

  # Make the choice (pass event info for better choice count detection)
  success = select_event_choice(choice_index, event_text, event_type)

  if success:
    print(f"[EVENT] Successfully selected choice {choice_index}")
  else:
    print(f"[EVENT] Failed to select choice {choice_index}")

  return success

# Event Data Collection and Smart Sampling Functions

def should_log_event(event_text: str, event_type: str = "unknown") -> bool:
  """
  Determine if we should log this event based on user settings
  Returns True if the event should be logged, False otherwise
  """
  if not EVENT_DATA_COLLECTION or not EVENT_DATA_COLLECTION.get("enabled", True):
    return False

  settings = EVENT_DATA_COLLECTION

  # Check event type filters
  event_types = settings.get("event_types", {})
  if event_type == "character" and not event_types.get("character_events", True):
    return False
  if event_type == "support" and not event_types.get("support_card_events", True):
    return False
  if event_type == "random" and not event_types.get("random_events", False):
    return False
  if event_type == "special" and not event_types.get("special_events", True):
    return False

  # Check minimum importance threshold
  importance = calculate_event_importance(event_text, event_type)
  min_threshold = settings.get("learning_features", {}).get("minimum_importance_threshold", 3)
  if importance < min_threshold:
    return False

  return True

def calculate_event_importance(event_text: str, event_type: str) -> int:
  """
  Calculate the importance score of an event based on keywords and context
  Returns an integer score (higher = more important)
  """
  score = 1  # Base score

  # Keyword-based scoring
  stat_keywords = ["スタミナ", "スピード", "パワー", "根性", "賢さ", "stat", "spd", "sta", "pwr", "guts", "wit"]
  skill_keywords = ["スキル", "skill", "才能", "talent"]
  mood_keywords = ["機嫌", "mood", "楽しい", "嬉しい", "happy"]
  relationship_keywords = ["絆", "bond", "relationship", "友情", "friendship"]

  event_lower = event_text.lower()

  # Stat-related events get higher priority
  for keyword in stat_keywords:
    if keyword in event_text:
      score += 3
      break

  # Skill gain events are very important
  for keyword in skill_keywords:
    if keyword in event_text:
      score += 4
      break

  # Mood improvement events are moderately important
  for keyword in mood_keywords:
    if keyword in event_text:
      score += 2
      break

  # Relationship events are important for long-term training
  for keyword in relationship_keywords:
    if keyword in event_text:
      score += 2
      break

  # Context-based modifiers
  if event_type == "character":
    score += 1  # Character events are generally more important
  elif event_type == "support":
    score += 1  # Support card events are also valuable

  # Current training priorities modifier
  if PRIORITY_STAT:
    primary_stat = PRIORITY_STAT[0]
    stat_keywords_map = {
      "sta": ["スタミナ", "sta", "stamina"],
      "spd": ["スピード", "spd", "speed"],
      "pwr": ["パワー", "pwr", "power"],
      "guts": ["根性", "guts"],
      "wit": ["賢さ", "wit", "intelligence"]
    }

    if primary_stat in stat_keywords_map:
      for keyword in stat_keywords_map[primary_stat]:
        if keyword in event_text:
          score += 2  # Bonus for events matching primary training focus
          break

  return score

def get_event_collection_summary() -> Dict[str, Any]:
  """
  Get a summary of current event data collection settings
  """
  if not EVENT_DATA_COLLECTION:
    return {"enabled": False}

  return {
    "enabled": EVENT_DATA_COLLECTION.get("enabled", True),
    "event_types_tracked": sum(1 for v in EVENT_DATA_COLLECTION.get("event_types", {}).values() if v),
    "data_types_collected": sum(1 for v in EVENT_DATA_COLLECTION.get("data_to_collect", {}).values() if v),
    "context_tracked": sum(1 for v in EVENT_DATA_COLLECTION.get("context_tracking", {}).values() if v),
    "learning_features": EVENT_DATA_COLLECTION.get("learning_features", {}),
    "importance_threshold": EVENT_DATA_COLLECTION.get("learning_features", {}).get("minimum_importance_threshold", 3)
  }

def get_character_info():
  """Get basic character information"""
  if CHARACTER_DATA:
    return {
      "name": CHARACTER_DATA.get("name", "Unknown"),
      "id": CHARACTER_DATA.get("id", "Unknown"),
      "has_events": len(get_character_events()) > 0
    }
  return None

def get_support_cards_info():
  """Get information about all selected support cards"""
  cards_info = []
  if SUPPORT_CARDS_DATA:
    for i, card_data in enumerate(SUPPORT_CARDS_DATA):
      if card_data:
        cards_info.append({
          "slot": i + 1,
          "name": card_data.get("name", "Unknown"),
          "id": card_data.get("id", "Unknown"),
          "has_events": len(card_data.get("events", [])) > 0
        })
      else:
        cards_info.append({
          "slot": i + 1,
          "name": None,
          "id": None,
          "has_events": False
        })
  return cards_info

# Check turn
def check_turn():
    turn = enhanced_screenshot(TURN_REGION)
    turn_text = extract_text(turn)

    if "Race Day" in turn_text:
        return "Race Day"

    # sometimes easyocr misreads characters instead of numbers
    cleaned_text = (
        turn_text
        .replace("T", "1")
        .replace("I", "1")
        .replace("O", "0")
        .replace("S", "5")
    )

    digits_only = re.sub(r"[^\d]", "", cleaned_text)

    if digits_only:
      return int(digits_only)
    
    return -1

# Check year
def check_current_year():
  year = enhanced_screenshot(YEAR_REGION)
  text = extract_text(year)
  return text

# Check criteria
def check_criteria():
  img = enhanced_screenshot(CRITERIA_REGION)
  text = extract_text(img)
  return text

def wait_for_user_intervention(timeout_seconds=None):
  """
  Wait for user to manually select an event choice within the timeout period.
  Returns the choice index (1-5) if user intervenes, None if timeout expires.
  """
  if timeout_seconds is None:
    # Get timeout directly from config to avoid global variable issues
    config = load_config()
    timeout_seconds = config.get("event_data_collection", {}).get("user_intervention_timeout", 10)

  print(f"[EVENT] Waiting {timeout_seconds} seconds for user intervention...")
  print("[EVENT] Click an event choice manually if you want to override the bot's decision")

  import time
  import pyautogui
  from core.recognizer import match_template

  start_time = time.time()
  last_check_time = 0
  last_countdown_time = 0

  while time.time() - start_time < timeout_seconds:
    # Check for user intervention every 0.5 seconds to avoid excessive CPU usage
    if time.time() - last_check_time >= 0.5:
      last_check_time = time.time()

      # Check if any event choice icons are still visible (event hasn't been handled yet)
      event_icons = [
        "assets/icons/event_choice_1.png",
        "assets/icons/event_choice_2.png",
        "assets/icons/event_choice_3.png",
        "assets/icons/event_choice_4.png",
        "assets/icons/event_choice_5.png"
      ]

      event_still_active = False
      for icon in event_icons:
        try:
          btn = pyautogui.locateCenterOnScreen(icon, confidence=0.7, minSearchTime=0.1)
          if btn:
            event_still_active = True
            break
        except:
          pass

      # If no event choices are visible, user might have made a choice
      if not event_still_active:
        print("[EVENT] Event choices no longer visible - user may have intervened")
        # Try to detect which choice was made by checking mouse position
        user_choice = detect_user_choice_from_mouse()
        if user_choice:
          print(f"[EVENT] Detected user selected choice {user_choice}")
          return user_choice
        else:
          return "user_intervened"

      # Show countdown every 2 seconds
      if time.time() - last_countdown_time >= 2:
        last_countdown_time = time.time()
        elapsed = int(time.time() - start_time)
        remaining = timeout_seconds - elapsed
        if remaining > 0:
          print(f"[EVENT] {remaining} seconds remaining for user intervention...")

    time.sleep(0.1)  # Small sleep to prevent excessive CPU usage

  print("[EVENT] Timeout expired - proceeding with automatic choice")
  return None

def detect_user_choice_from_mouse():
  """
  Try to detect which choice the user clicked based on mouse position
  Returns the choice number (1-5) or None if unable to determine
  """
  try:
    import pyautogui
    from core.execute import get_choice_position_by_coordinate

    # Get current mouse position
    mouse_x, mouse_y = pyautogui.position()

    # Check which choice position is closest to mouse position
    # We'll check a reasonable range around each choice position
    choice_positions = {}
    for choice_num in range(1, 6):  # Check choices 1-5
      try:
        pos = get_choice_position_by_coordinate(choice_num, 5)  # Assume 5 choices max
        if pos:
          choice_positions[choice_num] = pos
      except:
        pass

    # Find the closest choice to mouse position
    closest_choice = None
    min_distance = float('inf')

    for choice_num, (choice_x, choice_y) in choice_positions.items():
      distance = ((mouse_x - choice_x) ** 2 + (mouse_y - choice_y) ** 2) ** 0.5
      if distance < min_distance and distance < 50:  # Within 50 pixels
        min_distance = distance
        closest_choice = choice_num

    if closest_choice:
      print(f"[EVENT] Mouse position ({mouse_x}, {mouse_y}) closest to choice {closest_choice}")
      return closest_choice

  except Exception as e:
    print(f"[EVENT] Error detecting user choice from mouse: {e}")

  return None

def _log_user_choice_for_learning(event_text, user_choice, event_type, pre_stats, pre_mood, pre_year, support_cards):
  """Log user's manual choice for future learning"""
  try:
    import uuid
    from datetime import datetime

    # Create session ID for tracking
    session_id = str(uuid.uuid4())[:8]

    # Get current character info
    config = load_config()
    character = config.get("character", {}).get("name", "Unknown")

    # Event data structure for user learning
    event_data = {
      'session_id': session_id,
      'timestamp': datetime.now().isoformat(),
      'event_text': event_text,
      'detected_choices': [],  # Will be filled if we can detect them
      'choice_made': user_choice,
      'character': character,
      'support_cards': support_cards,
      'current_stats': pre_stats,
      'current_mood': pre_mood,
      'current_year': pre_year,
      'event_type': event_type,
      'user_intervention': True,  # Mark as user intervention
      'outcome': {}  # Will be updated after event completes
    }

    # Try to get choices from database for better analysis
    try:
      detected_choices = get_event_choices_from_database(event_text, event_type)
      if detected_choices:
        event_data['detected_choices'] = detected_choices
    except:
      pass

    # Save to JSON file
    success = _save_event_to_json(event_data)
    if success:
      print(f"[EVENT] Logged user choice {user_choice} for learning (session: {session_id})")
    else:
      print("[EVENT] Failed to log user choice to JSON")

  except Exception as e:
    print(f"[EVENT] Error logging user choice: {e}")

def detect_event_choices():
  """Detect available event choices using OCR"""
  try:
    from utils.screenshot import enhanced_screenshot
    from core.ocr import extract_text

    # Define choice text regions (these would need to be calibrated)
    # This is a placeholder - actual regions would need to be determined
    choice_regions = [
      (100, 400, 300, 50),  # Choice 1
      (100, 460, 300, 50),  # Choice 2
      (100, 520, 300, 50),  # Choice 3
      (100, 580, 300, 50),  # Choice 4
      (100, 640, 300, 50),  # Choice 5
    ]

    choices = []
    for i, region in enumerate(choice_regions):
      try:
        img = enhanced_screenshot(region)
        text = extract_text(img)
        if text and len(text.strip()) > 0:
          choices.append(text.strip())
      except:
        pass

    return choices

  except Exception as e:
    print(f"[EVENT] Error detecting choices: {e}")
    return []

def check_skill_pts():
    """Return the current skill points by reading the skill points region using OCR."""
    img = capture_region(SKILL_PTS_REGION)
    pts = extract_number(img)
    return pts if pts is not None else 0