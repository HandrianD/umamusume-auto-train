import pyautogui
import time
from PIL import ImageGrab

pyautogui.useImageNotFoundException(False)

import core.state as state
from core.state import check_support_card, check_failure, check_turn, check_mood, check_current_year, check_criteria, check_skill_pts, check_energy, get_current_energy_level
from core.logic import do_something
from core.ocr import extract_text
from utils.constants import MOOD_LIST, SCREEN_BOTTOM_REGION, CHOICE_AREA_REGION
from utils.screenshot import enhanced_screenshot

def is_valid_mouse_position(pos):
  """Check if mouse position is valid and won't trigger PyAutoGUI fail-safe"""
  if pos is None:
    return False

  try:
    x, y = pos
    screen_width, screen_height = pyautogui.size()

    # Check if position is within screen bounds
    if x < 10 or y < 10 or x > screen_width - 10 or y > screen_height - 10:
      print(f"[DEBUG] Invalid mouse position: {pos} (screen: {screen_width}x{screen_height})")
      return False

    return True
  except (TypeError, ValueError) as e:
    print(f"[DEBUG] Error validating mouse position {pos}: {e}")
    return False

def test_choice_4_coordinate():
  """
  Test function to verify choice 4 coordinate detection without clicking
  Returns the coordinate that would be clicked for choice 4, or None if not detected
  """
  print("[TEST] Starting choice 4 coordinate test...")
  
  try:
    # Take a screenshot to analyze
    screen = ImageGrab.grab()
    
    # Check for event detection
    templates = {
      "event": "assets/icons/event_choice_1.png"
    }
    
    matches = multi_match_templates(templates, screen=screen)
    
    # Check if event is detected
    if matches.get("event"):
      print("[TEST] Event detected - extracting event text...")
      
      # Extract event text - SPLIT INTO TWO REGIONS for better accuracy
      event_type_region = (150, 157, 634-150, 190-157)  # TOP: Event type
      event_title_region = (150, 190, 634-150, 241-190)  # BOTTOM: Event title
      
      event_type_screenshot = pyautogui.screenshot(region=event_type_region)
      event_title_screenshot = pyautogui.screenshot(region=event_title_region)
      
      event_type_text = extract_text(event_type_screenshot).strip()
      event_text = extract_text(event_title_screenshot).strip()  # Use title as main event text
      
      if event_text.strip():
        print(f"[TEST] Event type: '{event_type_text}'")
        print(f"[TEST] Extracted event text: '{event_text[:100]}...'")
        
        # Get intelligent choice recommendation
        optimal_choice = state.get_optimal_event_choice_from_database(event_text, "character")
        print(f"[TEST] Intelligence recommends: Choice {optimal_choice}")
        
        if optimal_choice == 4:
          print("[TEST] Choice 4 recommended! Testing coordinate detection...")
          
          # Detect number of choices
          num_choices, position_mapping = detect_number_of_choices()
          
          if num_choices:
            print(f"[TEST] Detected {num_choices} choices on screen")
          else:
            print("[TEST] Could not detect number of choices, using fallback")
          
          # Get the coordinate for choice 4
          choice_location = get_choice_position_by_coordinate(4, num_choices, position_mapping)
          
          if choice_location and is_valid_mouse_position(choice_location):
            print(f"[TEST] SUCCESS: Choice 4 coordinate detected at {choice_location}")
            print(f"[TEST] X: {choice_location[0]}, Y: {choice_location[1]}")
            
            # Stop the bot
            state.is_bot_running = False
            print("[TEST] Bot stopped for coordinate verification")
            
            return choice_location
          else:
            print("[TEST] FAILED: Could not determine valid coordinate for choice 4")
            return None
        else:
          print(f"[TEST] Intelligence recommends choice {optimal_choice}, not choice 4. Continuing...")
          return None
      else:
        print("[TEST] No event text extracted")
        return None
    else:
      print("[TEST] No event detected")
      return None
      
  except Exception as e:
    print(f"[TEST] Error during choice 4 test: {e}")
    return None
  """
  Detect how many event choices are currently visible on screen
  Returns the number of choices (1-5) or None if unable to detect
  """
  try:
    choice_templates = [
      "assets/icons/event_choice_1.png",
      "assets/icons/event_choice_2.png", 
      "assets/icons/event_choice_3.png",
      "assets/icons/event_choice_4.png",
      "assets/icons/event_choice_5.png"
    ]
    
    found_positions = []
    
    # Look for each choice template
    for i, template in enumerate(choice_templates, 1):
      try:
        location = pyautogui.locateCenterOnScreen(template, confidence=0.8, minSearchTime=0.5)
        if location:
          # Validate it's in the choice area (right side of screen, reasonable Y position)
          if location.x > 200 and 300 <= location.y <= 900:
            found_positions.append((i, location))
            print(f"[DEBUG] Found choice {i} template at {location}")
      except Exception as e:
        continue
    
    if not found_positions:
      print("[DEBUG] No choice templates found")
      return None, None
      
    # Sort by Y position to determine the actual choice order
    found_positions.sort(key=lambda x: x[1].y)
    
    num_choices = len(found_positions)
    print(f"[DEBUG] Detected {num_choices} choices on screen")
    
    # Map the found positions to choice numbers based on their vertical order
    position_mapping = {}
    for choice_num, (template_num, pos) in enumerate(found_positions, 1):
      position_mapping[choice_num] = (pos.x, pos.y)
      print(f"[DEBUG] Choice {choice_num} mapped to position {pos}")
    
    return num_choices, position_mapping
    
  except Exception as e:
    print(f"[ERROR] Failed to detect number of choices: {e}")
    return None, None

def detect_number_of_choices():
  """
  Detect how many event choices are currently visible on screen
  Returns the number of choices (1-5) or None if unable to detect
  """
  try:
    # First, try to find any event choice icons using a more general approach
    # Look for common choice icon patterns rather than specific numbered templates
    general_choice_patterns = [
      "assets/icons/event_choice_1.png",
      "assets/icons/event_choice_2.png",
      "assets/icons/event_choice_3.png",
      "assets/icons/event_choice_4.png",
      "assets/icons/event_choice_5.png"
    ]

    found_positions = []

    # Look for each choice template with lower confidence to catch variations
    for i, template in enumerate(general_choice_patterns, 1):
      try:
        # Try multiple confidence levels
        for confidence in [0.9, 0.8, 0.7, 0.6]:
          location = pyautogui.locateCenterOnScreen(template, confidence=confidence, minSearchTime=0.3)
          if location:
            # Validate it's in the choice area (right side of screen, reasonable Y position)
            if location.x > 150 and 250 <= location.y <= 900:
              found_positions.append((i, location, confidence))
              print(f"[DEBUG] Found choice template {i} at {location} (confidence: {confidence})")
              break  # Found it, move to next template
      except Exception as e:
        continue

    if not found_positions:
      print("[DEBUG] No choice templates found")
      return None, None

    # Remove duplicates (same position found by multiple templates)
    unique_positions = []
    for template_num, pos, confidence in found_positions:
      # Check if this position is already found (within 20 pixels)
      is_duplicate = False
      for _, existing_pos, _ in unique_positions:
        if abs(pos.x - existing_pos.x) < 20 and abs(pos.y - existing_pos.y) < 20:
          is_duplicate = True
          break
      if not is_duplicate:
        unique_positions.append((template_num, pos, confidence))

    print(f"[DEBUG] Found {len(unique_positions)} unique choice positions")

    # Sort by Y position to determine the actual choice order
    unique_positions.sort(key=lambda x: x[1].y)

    num_choices = len(unique_positions)
    print(f"[DEBUG] Detected {num_choices} choices on screen")

    # Map the found positions to choice numbers based on their vertical order
    position_mapping = {}
    for choice_num, (template_num, pos, confidence) in enumerate(unique_positions, 1):
      position_mapping[choice_num] = (pos.x, pos.y)
      print(f"[DEBUG] Choice {choice_num} mapped to position {pos} (from template {template_num}, conf: {confidence})")

    return num_choices, position_mapping

  except Exception as e:
    print(f"[ERROR] Failed to detect number of choices: {e}")
    return None, None

def get_choice_position_by_coordinate(choice_number, num_choices=None, position_mapping=None):
  """
  Get choice position based on measured screen coordinates
  Adapts to the actual number of choices present
  """
  try:
    # If we have detected positions, use them
    if position_mapping and choice_number in position_mapping:
      position = position_mapping[choice_number]
      print(f"[DEBUG] Using detected position for choice {choice_number}: {position}")
      if is_valid_mouse_position(position):
        return position
    
    # Fallback to measured coordinates based on number of choices
    if num_choices is None:
      # Default to 5 choices if we can't detect
      num_choices = 5
      print(f"[DEBUG] Could not detect number of choices, defaulting to {num_choices}")
    
    # Choice positions based on number of choices
    if num_choices == 2:
      # For 2 choices, they appear at positions 4 and 5
      choice_positions = {
        1: (290, 644),  # Choice 1 at position 4
        2: (290, 755),  # Choice 2 at position 5
      }
    elif num_choices == 3:
      # For 3 choices, they appear at positions 3, 4, and 5
      choice_positions = {
        1: (300, 532),  # Choice 1 at position 3
        2: (300, 644),  # Choice 2 at position 4
        3: (300, 755),  # Choice 3 at position 5
      }
    elif num_choices == 4:
      # For 4 choices, they appear at positions 2, 3, 4, and 5
      choice_positions = {
        1: (300, 421),  # Choice 1 at position 2
        2: (300, 532),  # Choice 2 at position 3
        3: (300, 644),  # Choice 3 at position 4
        4: (300, 755),  # Choice 4 at position 5
      }
    else:  # num_choices == 5 or unknown
      # For 5 choices, use all positions
      choice_positions = {
        1: (300, 310),  # Choice 1
        2: (300, 421),  # Choice 2  
        3: (300, 532),  # Choice 3
        4: (300, 644),  # Choice 4
        5: (300, 755),  # Choice 5
      }
    
    if choice_number not in choice_positions:
      print(f"[WARNING] Invalid choice number {choice_number}, must be 1-{num_choices}")
      return None
    
    position = choice_positions[choice_number]
    print(f"[DEBUG] Using measured position for choice {choice_number} (detected {num_choices} choices): {position}")
    
    # Validate the position
    if is_valid_mouse_position(position):
      return position
    else:
      print(f"[WARNING] Position {position} failed validation")
      return None
      
  except Exception as e:
    print(f"[ERROR] Failed to get choice position: {e}")
    return None

def test_choice_2_with_2_choices():
  """
  Test function to verify choice 2 coordinate detection when there are only 2 choices
  This tests the specific scenario where choices reposition to the bottom
  """
  print("[TEST] Starting choice 2 test for 2-choice scenarios...")
  
  try:
    # Check for event detection by looking for choice templates
    choice_templates = [
      "assets/icons/event_choice_1.png",
      "assets/icons/event_choice_2.png", 
      "assets/icons/event_choice_3.png",
      "assets/icons/event_choice_4.png",
      "assets/icons/event_choice_5.png"
    ]
    
    found_choices = []
    for i, template in enumerate(choice_templates, 1):
      try:
        location = pyautogui.locateCenterOnScreen(template, confidence=0.8, minSearchTime=0.5)
        if location and location.x > 200 and 300 <= location.y <= 900:
          found_choices.append((i, location))
          print(f"[TEST] Found choice {i} at {location}")
      except Exception as e:
        continue
    
    if len(found_choices) >= 2:
      print(f"[TEST] Event detected with {len(found_choices)} choices - extracting event text...")
      
      # Extract event text
      event_region = (150, 157, 634-150, 241-157)
      event_screenshot = pyautogui.screenshot(region=event_region)
      event_text = extract_text(event_screenshot)
      
      if event_text.strip():
        print(f"[TEST] Extracted event text: '{event_text[:100]}...'")
        
        # Get intelligent choice recommendation
        optimal_choice = state.get_optimal_event_choice_from_database(event_text, "character")
        print(f"[TEST] Intelligence recommends: Choice {optimal_choice}")
        
        # Force test choice 2 for 2-choice scenarios
        if len(found_choices) == 2 and optimal_choice == 2:
          print("[TEST] 2-choice scenario detected! Testing choice 2 positioning...")
          
          # For 2 choices, use the repositioned coordinates
          print("[TEST] Using 2-choice repositioned coordinates...")
          print("[TEST] Choice 1 should be at position 4: (290, 644)")
          print("[TEST] Choice 2 should be at position 5: (290, 755)")
          
          # Get the coordinate for choice 2 in 2-choice scenario
          choice_location = get_choice_position_by_coordinate(2, 2, None)  # Force 2 choices
          
          if choice_location and is_valid_mouse_position(choice_location):
            print(f"[TEST] SUCCESS: Choice 2 coordinate for 2-choice scenario: {choice_location}")
            print(f"[TEST] X: {choice_location[0]}, Y: {choice_location[1]}")
            
            # Move cursor to the position for visual verification
            print(f"[TEST] Moving cursor to choice 2 position in 2-choice scenario...")
            pyautogui.moveTo(choice_location[0], choice_location[1], duration=0.5)
            print(f"[TEST] ✅ Cursor moved to {choice_location} - verify this is choice 2 in 2-choice layout")
            
            # Stop the bot
            state.is_bot_running = False
            print("[TEST] Bot stopped - check if cursor is over choice 2 in the 2-choice layout")
            
            return choice_location
          else:
            print("[TEST] FAILED: Could not determine valid coordinate for choice 2 in 2-choice scenario")
            return None
        elif len(found_choices) == 2:
          print(f"[TEST] 2-choice scenario but intelligence recommends choice {optimal_choice}, not choice 2")
          print("[TEST] Wait for an event where intelligence recommends choice 2 with 2 choices")
          return None
        else:
          print(f"[TEST] {len(found_choices)} choices detected, not a 2-choice scenario")
          return None
      else:
        print("[TEST] No event text extracted")
        return None
    else:
      print(f"[TEST] No event detected (found {len(found_choices)} choices, need at least 2)")
      return None
      
  except Exception as e:
    print(f"[TEST] Error during 2-choice test: {e}")
    return None

def test_choice_4_with_cursor():
  """
  Test function to verify choice 4 coordinate detection WITH cursor movement
  Moves cursor to detected position for visual verification and stops bot
  """
  print("[TEST] Starting choice 4 coordinate test with cursor movement...")
  
  try:
    # Check for event detection by looking for choice templates
    choice_templates = [
      "assets/icons/event_choice_1.png",
      "assets/icons/event_choice_2.png", 
      "assets/icons/event_choice_3.png",
      "assets/icons/event_choice_4.png",
      "assets/icons/event_choice_5.png"
    ]
    
    found_choices = []
    for i, template in enumerate(choice_templates, 1):
      try:
        location = pyautogui.locateCenterOnScreen(template, confidence=0.8, minSearchTime=0.5)
        if location and location.x > 200 and 300 <= location.y <= 900:
          found_choices.append((i, location))
          print(f"[TEST] Found choice {i} at {location}")
      except Exception as e:
        continue
    
    if len(found_choices) >= 2:
      print(f"[TEST] Event detected with {len(found_choices)} choices - extracting event text...")
      
      # Extract event text
      event_region = (150, 157, 634-150, 241-157)
      event_screenshot = pyautogui.screenshot(region=event_region)
      event_text = extract_text(event_screenshot)
      
      if event_text.strip():
        print(f"[TEST] Extracted event text: '{event_text[:100]}...'")
        
        # Get intelligent choice recommendation
        optimal_choice = state.get_optimal_event_choice_from_database(event_text, "character")
        print(f"[TEST] Intelligence recommends: Choice {optimal_choice}")
        
        if optimal_choice == 4:
          print("[TEST] Choice 4 recommended! Using coordinate-based approach...")
          
          # Use coordinate-based detection with user's measured positions
          print("[TEST] Using measured coordinates...")
          
          # Get the coordinate for choice 4 using measured positions
          choice_location = get_choice_position_by_coordinate(4, None, None)  # No template detection needed
          
          if choice_location and is_valid_mouse_position(choice_location):
            print(f"[TEST] SUCCESS: Choice 4 coordinate set to measured position: {choice_location}")
            print(f"[TEST] X: {choice_location[0]}, Y: {choice_location[1]}")
            
            # Move cursor to the measured position for visual verification
            print(f"[TEST] Moving cursor to choice 4 measured position...")
            pyautogui.moveTo(choice_location[0], choice_location[1], duration=0.5)
            print(f"[TEST] ✅ Cursor moved to {choice_location} - verify this is choice 4 position")
            
            # Stop the bot
            state.is_bot_running = False
            print("[TEST] Bot stopped for coordinate verification")
            
            return choice_location
          else:
            print("[TEST] FAILED: Could not determine valid coordinate for choice 4")
            return None
        else:
          print(f"[TEST] Intelligence recommends choice {optimal_choice}, not choice 4. Continuing...")
          return None
      else:
        print("[TEST] No event text extracted")
        return None
    else:
      print("[TEST] No event detected")
      return None
      
  except Exception as e:
    print(f"[TEST] Error during choice 4 test: {e}")
    return None

def multi_match_templates(templates, screen=None):
  """
  Perform multi-template matching on the screen
  Returns a dictionary of template names to list of (x, y, w, h) boxes
  """
  matches = {}
  
  for name, template_path in templates.items():
    try:
      # Use pyautogui to find all instances of the template
      locations = list(pyautogui.locateAllOnScreen(template_path, confidence=0.8, grayscale=True))
      if locations:
        # Convert Location objects to (x, y, w, h) tuples
        boxes = []
        for loc in locations:
          boxes.append((loc.left, loc.top, loc.width, loc.height))
        matches[name] = boxes
        print(f"[DEBUG] Found {len(boxes)} instances of {name}")
      else:
        matches[name] = []
    except Exception as e:
      print(f"[DEBUG] Error matching template {name}: {e}")
      matches[name] = []
      
  return matches

def test_choice_4_coordinate():
  """
  Detect how many event choices are currently visible on screen
  Returns the number of choices (1-5) or None if unable to detect
  """
  try:
    choice_templates = [
      "assets/icons/event_choice_1.png",
      "assets/icons/event_choice_2.png", 
      "assets/icons/event_choice_3.png",
      "assets/icons/event_choice_4.png",
      "assets/icons/event_choice_5.png"
    ]
    
    found_positions = []
    
    # Look for each choice template
    for i, template in enumerate(choice_templates, 1):
      try:
        location = pyautogui.locateCenterOnScreen(template, confidence=0.8, minSearchTime=0.5)
        if location:
          # Validate it's in the choice area (right side of screen, reasonable Y position)
          if location.x > 200 and 300 <= location.y <= 900:
            found_positions.append((i, location))
            print(f"[DEBUG] Found choice {i} template at {location}")
      except Exception as e:
        continue
    
    if not found_positions:
      print("[DEBUG] No choice templates found")
      return None, None
      
    # Sort by Y position to determine the actual choice order
    found_positions.sort(key=lambda x: x[1].y)
    
    num_choices = len(found_positions)
    print(f"[DEBUG] Detected {num_choices} choices on screen")
    
    # Map the found positions to choice numbers based on their vertical order
    position_mapping = {}
    for choice_num, (template_num, pos) in enumerate(found_positions, 1):
      position_mapping[choice_num] = (pos.x, pos.y)
      print(f"[DEBUG] Choice {choice_num} mapped to position {pos}")
    
    return num_choices, position_mapping
    
  except Exception as e:
    print(f"[ERROR] Failed to detect number of choices: {e}")
    return None, None

def test_choice_4_coordinate():
  """
  Test function to verify choice 4 coordinate detection without clicking
  Returns the coordinate that would be clicked for choice 4, or None if not detected
  """
  print("[TEST] Starting choice 4 coordinate test...")
  
  try:
    # Take a screenshot to analyze
    screen = ImageGrab.grab()
    
    # Check for event detection
    templates = {
      "event": "assets/icons/event.png",
    }
    
    matches = multi_match_templates(templates, screen=screen)
    
    # Check if event is detected
    if matches.get("event"):
      print("[TEST] Event detected - extracting event text...")
      
      # Extract event text
      event_region = (150, 157, 634-150, 241-157)
      event_screenshot = pyautogui.screenshot(region=event_region)
      event_text = extract_text(event_screenshot)
      
      if event_text.strip():
        print(f"[TEST] Extracted event text: '{event_text[:100]}...'")
        
        # Get intelligent choice recommendation
        optimal_choice = state.get_optimal_event_choice_from_database(event_text, "character")
        print(f"[TEST] Intelligence recommends: Choice {optimal_choice}")
        
        if optimal_choice == 4:
          print("[TEST] Choice 4 recommended! Testing coordinate detection...")
          
          # Detect number of choices
          num_choices, position_mapping = detect_number_of_choices()
          
          if num_choices:
            print(f"[TEST] Detected {num_choices} choices on screen")
          else:
            print("[TEST] Could not detect number of choices, using fallback")
          
          # Get the coordinate for choice 4
          choice_location = get_choice_position_by_coordinate(4, num_choices, position_mapping)
          
          if choice_location and is_valid_mouse_position(choice_location):
            print(f"[TEST] SUCCESS: Choice 4 coordinate detected at {choice_location}")
            print(f"[TEST] X: {choice_location[0]}, Y: {choice_location[1]}")
            
            # Stop the bot
            state.is_bot_running = False
            print("[TEST] Bot stopped for coordinate verification")
            
            return choice_location
          else:
            print("[TEST] FAILED: Could not determine valid coordinate for choice 4")
            return None
        else:
          print(f"[TEST] Intelligence recommends choice {optimal_choice}, not choice 4. Continuing...")
          return None
      else:
        print("[TEST] No event text extracted")
        return None
    else:
      print("[TEST] No event detected")
      return None
      
  except Exception as e:
    print(f"[TEST] Error during choice 4 test: {e}")
    return None
  """
  Detect how many event choices are currently visible on screen
  Returns the number of choices (1-5) or None if unable to detect
  """
  try:
    choice_templates = [
      "assets/icons/event_choice_1.png",
      "assets/icons/event_choice_2.png", 
      "assets/icons/event_choice_3.png",
      "assets/icons/event_choice_4.png",
      "assets/icons/event_choice_5.png"
    ]
    
    found_positions = []
    
    # Look for each choice template
    for i, template in enumerate(choice_templates, 1):
      try:
        location = pyautogui.locateCenterOnScreen(template, confidence=0.8, minSearchTime=0.5)
        if location:
          # Validate it's in the choice area (right side of screen, reasonable Y position)
          if location.x > 200 and 300 <= location.y <= 900:
            found_positions.append((i, location))
            print(f"[DEBUG] Found choice {i} template at {location}")
      except Exception as e:
        continue
    
    if not found_positions:
      print("[DEBUG] No choice templates found")
      return None
      
    # Sort by Y position to determine the actual choice order
    found_positions.sort(key=lambda x: x[1].y)
    
    num_choices = len(found_positions)
    print(f"[DEBUG] Detected {num_choices} choices on screen")
    
    # Map the found positions to choice numbers based on their vertical order
    position_mapping = {}
    for choice_num, (template_num, pos) in enumerate(found_positions, 1):
      position_mapping[choice_num] = (pos.x, pos.y)
      print(f"[DEBUG] Choice {choice_num} mapped to position {pos}")
    
    return num_choices, position_mapping
    
  except Exception as e:
    print(f"[ERROR] Failed to detect number of choices: {e}")
    return None, None

def get_choice_position_by_coordinate(choice_number, num_choices=None, position_mapping=None):
  """
  Get choice position based on measured screen coordinates
  Adapts to the actual number of choices present
  """
  try:
    # If we have detected positions, use them
    if position_mapping and choice_number in position_mapping:
      position = position_mapping[choice_number]
      print(f"[DEBUG] Using detected position for choice {choice_number}: {position}")
      if is_valid_mouse_position(position):
        return position
    
    # Fallback to measured coordinates based on number of choices
    if num_choices is None:
      # Default to 5 choices if we can't detect
      num_choices = 5
      print(f"[DEBUG] Could not detect number of choices, defaulting to {num_choices}")
    
    # Choice positions based on number of choices
    if num_choices == 2:
      # For 2 choices, they appear at positions 4 and 5
      choice_positions = {
        1: (290, 644),  # Choice 1 at position 4
        2: (290, 755),  # Choice 2 at position 5
      }
    elif num_choices == 3:
      # For 3 choices, they appear at positions 3, 4, and 5
      choice_positions = {
        1: (300, 532),  # Choice 1 at position 3
        2: (300, 644),  # Choice 2 at position 4
        3: (300, 755),  # Choice 3 at position 5
      }
    elif num_choices == 4:
      # For 4 choices, they appear at positions 2, 3, 4, and 5
      choice_positions = {
        1: (300, 421),  # Choice 1 at position 2
        2: (300, 532),  # Choice 2 at position 3
        3: (300, 644),  # Choice 3 at position 4
        4: (300, 755),  # Choice 4 at position 5
      }
    else:  # num_choices == 5 or unknown
      # For 5 choices, use all positions
      choice_positions = {
        1: (300, 310),  # Choice 1
        2: (300, 421),  # Choice 2  
        3: (300, 532),  # Choice 3
        4: (300, 644),  # Choice 4
        5: (300, 755),  # Choice 5
      }
    
    if choice_number not in choice_positions:
      print(f"[WARNING] Invalid choice number {choice_number}, must be 1-{num_choices}")
      return None
    
    position = choice_positions[choice_number]
    print(f"[DEBUG] Using fallback position for choice {choice_number} (detected {num_choices} choices): {position}")
    
    # Validate the position
    if is_valid_mouse_position(position):
      return position
    else:
      print(f"[WARNING] Position {position} failed validation")
      return None
      
  except Exception as e:
    print(f"[ERROR] Failed to get choice position: {e}")
    return None

# Event detection cooldown to prevent false positives
last_event_detection_time = 0
EVENT_DETECTION_COOLDOWN = 5  # seconds
event_detection_count = 0
last_minute_start = 0

def is_race_results_screen():
  """
  Check if we're currently on a race results or post-race screen
  Returns True if race-related UI elements are detected
  """
  from core.ocr import extract_text
  from utils.constants import CHOICE_AREA_REGION, EVENT_TEXT_REGION

  # Try multiple regions where race results text might appear
  regions_to_check = [
    CHOICE_AREA_REGION,  # Original choice area
    EVENT_TEXT_REGION,   # Event text area
    (100, 100, 800, 600),  # Large upper area
    (200, 200, 1000, 800), # Large central area
    (0, 800, 1920, 280),  # Bottom area for race results
  ]

  race_indicators = [
    'turns until', 'next race', 'let\'s do it', 'debut', 'junior',
    'goals achieved', 'next goal', 'clear', 'g1', 'g2', 'g3',
    'place top', 'race results', 'ranking', 'position', 'finish',
    '1st', '2nd', '3rd', '4th', '5th', 'race day', 'results',
    'congratulations', 'victory', 'defeat', 'win', 'lose', 'this was a victory',
    'as the empress', 'my wish is to', 'always strive', 'standard'
  ]

  for i, region in enumerate(regions_to_check):
    try:
      print(f"[DEBUG] Checking region {i+1}: {region}")
      choice_img = enhanced_screenshot(region)
      choice_text = extract_text(choice_img)

      if choice_text:
        print(f"[DEBUG] Region {i+1} OCR text: '{choice_text[:100]}...'")
        lower_text = choice_text.lower()

        found_indicators = [indicator for indicator in race_indicators if indicator in lower_text]
        if found_indicators:
          print(f"[EVENT] Race results screen detected in region {i+1}: '{choice_text[:50]}...' (found: {found_indicators})")
          return True

        # Try fuzzy matching
        for indicator in race_indicators:
          if indicator.replace(' ', '') in lower_text.replace(' ', ''):
            print(f"[EVENT] Race results screen detected with fuzzy match in region {i+1}: '{indicator}' in '{choice_text[:50]}...'")
            return True
      else:
        print(f"[DEBUG] Region {i+1}: No text extracted")

    except Exception as e:
      print(f"[ERROR] Failed to check region {i+1}: {e}")

  print("[DEBUG] No race results indicators found in any region")
  return False

def is_post_race_navigation_screen():
  """
  Check if we're on a post-race screen that requires different navigation
  This screen often has decorative elements that look like event choices but aren't
  """
  # Add cooldown to prevent excessive OCR calls
  current_time = time.time()
  if hasattr(is_post_race_navigation_screen, '_last_call') and \
     current_time - is_post_race_navigation_screen._last_call < 2.0:
    return is_post_race_navigation_screen._last_result

  from core.ocr import extract_text

  post_race_indicators = [
    'continue', 'back to training', 'next turn', 'return to lobby',
    'training menu', 'career lobby', 'main menu', 'this was a victory',
    'victory', 'defeat', 'race result', 'finish line', 'goal achieved',
    'congratulations', 'well done', 'next race', 'training continues',
    'as the empress', 'my wish is to', 'always strive', 'standard',
    'performance', 'result', 'outcome'
  ]

  # Check bottom portion of screen for navigation text
  screen_width, screen_height = pyautogui.size()
  bottom_region = (0, screen_height - 300, screen_width, 300)

  try:
    screenshot = pyautogui.screenshot(region=bottom_region)
    text = extract_text(screenshot)

    result = False
    if text:
      lower_text = text.lower()
      print(f"[DEBUG] Post-race screen check - bottom text: '{text[:100]}...'")

      found_indicators = [indicator for indicator in post_race_indicators if indicator in lower_text]
      print(f"[DEBUG] Found post-race indicators: {found_indicators}")

      if found_indicators:
        print(f"[DEBUG] Post-race navigation screen detected: {found_indicators}")
        result = True

      # Check for common post-race UI patterns
      if 'next' in lower_text and ('turn' in lower_text or 'training' in lower_text):
        print("[DEBUG] Post-race screen detected: 'next' with turn/training context")
        result = True

    else:
      print("[DEBUG] No text detected in post-race screen check")

    # Store result for cooldown
    is_post_race_navigation_screen._last_call = current_time
    is_post_race_navigation_screen._last_result = result
    return result

  except Exception as e:
    print(f"[ERROR] Failed to check post-race screen: {e}")
    return False

  except Exception as e:
    print(f"[ERROR] Failed to check post-race screen: {e}")

  return False
from core.recognizer import is_btn_active, match_template, multi_match_templates
from utils.scenario import ura
from core.skill import buy_skill

templates = {
  "event": "assets/icons/event_choice_1.png",  # Used to detect event presence (generic)
  "inspiration": "assets/buttons/inspiration_btn.png",
  "next": "assets/buttons/next_btn.png",
  "next2": "assets/buttons/next2_btn.png",
  "cancel": "assets/buttons/cancel_btn.png",
  "tazuna": "assets/ui/tazuna_hint.png",
  "infirmary": "assets/buttons/infirmary_btn.png",
  "retry": "assets/buttons/retry_btn.png"
}

def click(img: str = None, confidence: float = 0.8, minSearch:float = 2, click: int = 1, text: str = "", boxes = None):
  if not state.is_bot_running:
    return False

  if boxes:
    if isinstance(boxes, list):
      if len(boxes) == 0:
        return False
      box = boxes[0]
    else :
      box = boxes

    if text:
      print(text)
    x, y, w, h = box
    center = (x + w // 2, y + h // 2)
    print(f"[DEBUG] Clicking at center: {center} from box: {box}")
    
    # Check if the button area looks clickable (not grayed out)
    try:
      button_region = (x, y, w, h)
      button_screenshot = pyautogui.screenshot(region=button_region)
      # Convert to grayscale and check average brightness
      grayscale = button_screenshot.convert('L')
      pixels = list(grayscale.getdata())
      avg_brightness = sum(pixels) / len(pixels)
      print(f"[DEBUG] Button area average brightness: {avg_brightness:.1f}")
      
      if avg_brightness < 100:
        print("[DEBUG] Button appears dark/disabled - may not be clickable")
      elif avg_brightness > 200:
        print("[DEBUG] Button appears bright/active - should be clickable")
      else:
        print("[DEBUG] Button brightness is moderate")
    except Exception as e:
      print(f"[DEBUG] Error checking button appearance: {e}")
    
    # Try multiple click attempts with slight variations
    for attempt in range(3):
      try:
        if attempt == 0:
          # First attempt: exact center
          click_x, click_y = center
        elif attempt == 1:
          # Second attempt: slightly offset
          click_x, click_y = center[0] + 10, center[1] + 5
        else:
          # Third attempt: slightly offset in other direction
          click_x, click_y = center[0] - 10, center[1] - 5
        
        pyautogui.moveTo(click_x, click_y, duration=0.1)
        pyautogui.click(clicks=click)
        print(f"[DEBUG] Click attempt {attempt + 1} at ({click_x}, {click_y})")
        time.sleep(0.2)  # Brief pause between attempts
      except Exception as e:
        print(f"[DEBUG] Click attempt {attempt + 1} failed: {e}")
    
    return True

  if img is None:
    return False

  print(f"[DEBUG] Looking for image: {img}")
  btn = pyautogui.locateCenterOnScreen(img, confidence=confidence, minSearchTime=minSearch)
  if btn and is_valid_mouse_position(btn):
    if text:
      print(text)
    pyautogui.moveTo(btn, duration=0.175)
    pyautogui.click(clicks=click)
    return True
  else:
    if btn:
      print(f"[DEBUG] Found button at {btn} but position is invalid")
    else:
      print(f"[DEBUG] Image {img} not found on screen")
  
  return False

def go_to_training():
  print("[DEBUG] Looking for training button...")
  result = click("assets/buttons/training_btn.png", text="[INFO] Training button found and clicked.")
  if not result:
    print("[DEBUG] Training button not found on screen")
  return result

def check_training():
  training_types = {
    "spd": "assets/icons/train_spd.png",
    "sta": "assets/icons/train_sta.png",
    "pwr": "assets/icons/train_pwr.png",
    "guts": "assets/icons/train_guts.png",
    "wit": "assets/icons/train_wit.png"
  }
  results = {}
  
  fail_check_states="train","no_train","check_all"

  failcheck="check_all"
  margin=5
  for key, icon_path in training_types.items():
    pos = pyautogui.locateCenterOnScreen(icon_path, confidence=0.8, region=SCREEN_BOTTOM_REGION)
    if pos and is_valid_mouse_position(pos):
      pyautogui.moveTo(pos, duration=0.1)
      pyautogui.mouseDown()
      support_counts = check_support_card()
      total_support = sum(support_counts.values())
      print(f"failcheck: {failcheck}")
      if key != "wit":
        if failcheck == "check_all":
          failure_chance = check_failure()
          if failure_chance > (state.MAX_FAILURE + margin):
            print("Failure rate too high skip to check wit")
            failcheck="no_train"
            failure_chance = state.MAX_FAILURE + margin
          elif failure_chance < (state.MAX_FAILURE - margin):
            print("Failure rate is low enough, skipping the rest of failure checks.")
            failcheck="train"
            failure_chance = 0
        elif failcheck == "no_train":
          failure_chance = state.MAX_FAILURE + margin
        elif failcheck == "train":
          failure_chance = 0
      else:
        if failcheck == "train":
          failure_chance = 0
        else:
          failure_chance = check_failure()
      results[key] = {
        "support": support_counts,
        "total_support": total_support,
        "failure": failure_chance
      }
      print(f"[{key.upper()}] → {support_counts}, Fail: {failure_chance}%")
      time.sleep(0.1)
    else:
      print(f"[DEBUG] Could not find valid position for {key} training icon")
      results[key] = {
        "support": {},
        "total_support": 0,
        "failure": 0
      }
  
  pyautogui.mouseUp()
  click(img="assets/buttons/back_btn.png")
  return results

def do_train(train):
  train_btn = pyautogui.locateCenterOnScreen(f"assets/icons/train_{train}.png", confidence=0.8, region=SCREEN_BOTTOM_REGION)
  if train_btn and is_valid_mouse_position(train_btn):
    pyautogui.tripleClick(train_btn, interval=0.1, duration=0.2)
  else:
    print(f"[DEBUG] Could not find valid position for {train} training button")

def do_rest():
  rest_btn = pyautogui.locateCenterOnScreen("assets/buttons/rest_btn.png", confidence=0.8, region=SCREEN_BOTTOM_REGION)
  rest_summber_btn = pyautogui.locateCenterOnScreen("assets/buttons/rest_summer_btn.png", confidence=0.8, region=SCREEN_BOTTOM_REGION)

  if rest_btn and is_valid_mouse_position(rest_btn):
    pyautogui.moveTo(rest_btn, duration=0.15)
    pyautogui.click(rest_btn)
  elif rest_summber_btn and is_valid_mouse_position(rest_summber_btn):
    pyautogui.moveTo(rest_summber_btn, duration=0.15)
    pyautogui.click(rest_summber_btn)
  else:
    print("[DEBUG] Could not find valid position for rest button")

def do_recreation():
  recreation_btn = pyautogui.locateCenterOnScreen("assets/buttons/recreation_btn.png", confidence=0.8, region=SCREEN_BOTTOM_REGION)
  recreation_summer_btn = pyautogui.locateCenterOnScreen("assets/buttons/rest_summer_btn.png", confidence=0.8, region=SCREEN_BOTTOM_REGION)

  if recreation_btn and is_valid_mouse_position(recreation_btn):
    pyautogui.moveTo(recreation_btn, duration=0.15)
    pyautogui.click(recreation_btn)
  elif recreation_summer_btn and is_valid_mouse_position(recreation_summer_btn):
    pyautogui.moveTo(recreation_summer_btn, duration=0.15)
    pyautogui.click(recreation_summer_btn)
  else:
    print("[DEBUG] Could not find valid position for recreation button")

def do_race(prioritize_g1 = False):
  click(img="assets/buttons/races_btn.png", minSearch=10)  

  consecutive_cancel_btn = pyautogui.locateCenterOnScreen("assets/buttons/cancel_btn.png", minSearchTime=0.7, confidence=0.8)
  if state.CANCEL_CONSECUTIVE_RACE and consecutive_cancel_btn:
    click(img="assets/buttons/cancel_btn.png", text="[INFO] Already raced 3+ times consecutively. Cancelling race and doing training.")
    return False
  elif not state.CANCEL_CONSECUTIVE_RACE and consecutive_cancel_btn:
    click(img="assets/buttons/ok_btn.png", minSearch=0.7)

  time.sleep(0.7)
  found = race_select(prioritize_g1=prioritize_g1)
  if not found:
    print("[INFO] No race found.")
    return False

  race_prep()
  time.sleep(0.3)
  after_race()
  return True

def race_day():
  click(img="assets/buttons/race_day_btn.png", minSearch=10)
  
  click(img="assets/buttons/ok_btn.png")
  time.sleep(0.5)

  for i in range(2):
    click(img="assets/buttons/race_btn.png", minSearch=2)
    time.sleep(0.5)

  race_prep()
  time.sleep(0.3)
  after_race()

def race_select(prioritize_g1 = False):
  # Move to safe position first
  safe_pos = (560, 680)
  if is_valid_mouse_position(safe_pos):
    pyautogui.moveTo(x=560, y=680)
  else:
    print("[DEBUG] Safe position (560, 680) is invalid, skipping initial move")

  time.sleep(0.2)

  if prioritize_g1:
    print("[INFO] Looking for G1 race.")
    for i in range(2):
      race_card = match_template("assets/ui/g1_race.png", threshold=0.9)

      if race_card:
        for x, y, w, h in race_card:
          region = (x, y, 310, 90)
          match_aptitude = pyautogui.locateCenterOnScreen("assets/ui/match_track.png", confidence=0.8, minSearchTime=0.7, region=region)
          if match_aptitude and is_valid_mouse_position(match_aptitude):
            print("[INFO] G1 race found.")
            pyautogui.moveTo(match_aptitude, duration=0.2)
            pyautogui.click()
            for i in range(2):
              click(img="assets/buttons/race_btn.png")
              time.sleep(0.5)
            return True
      
      for i in range(4):
        pyautogui.scroll(-300)
    
    return False
  else:
    print("[INFO] Looking for race.")
    for i in range(4):
      match_aptitude = pyautogui.locateCenterOnScreen("assets/ui/match_track.png", confidence=0.8, minSearchTime=0.7)
      if match_aptitude and is_valid_mouse_position(match_aptitude):
        print("[INFO] Race found.")
        pyautogui.moveTo(match_aptitude, duration=0.2)
        pyautogui.click(match_aptitude)

        for i in range(2):
          click(img="assets/buttons/race_btn.png")
          time.sleep(0.5)
        return True
      
      for i in range(4):
        pyautogui.scroll(-300)
    
    return False

def race_prep():
  view_result_btn = pyautogui.locateCenterOnScreen("assets/buttons/view_results.png", confidence=0.8, minSearchTime=10)
  if view_result_btn:
    pyautogui.click(view_result_btn)
    time.sleep(0.5)
    for i in range(3):
      pyautogui.tripleClick(interval=0.2)
      time.sleep(0.5)

def after_race():
  click(img="assets/buttons/next_btn.png", minSearch=5)
  time.sleep(0.3)
  pyautogui.click()
  click(img="assets/buttons/next2_btn.png", minSearch=5)

def auto_buy_skill():
  if check_skill_pts() < state.SKILL_PTS_CHECK:
    return

  click(img="assets/buttons/skills_btn.png")
  print("[INFO] Buying skills")
  time.sleep(0.5)

  if buy_skill():
    click(img="assets/buttons/confirm_btn.png", minSearch=0.5)
    click(img="assets/buttons/learn_btn.png", minSearch=0.5)
    time.sleep(0.5)
    click(img="assets/buttons/close_btn.png", minSearch=2)
    time.sleep(0.5)
    click(img="assets/buttons/back_btn.png")
  else:
    print("[INFO] No matching skills found. Going back.")
    click(img="assets/buttons/back_btn.png")

def select_event_choice(choice_index, event_text=None, event_type=None):
  """
  Select event choice using DATABASE-FIRST approach with user wait fallback
  Priority: Database → User Wait (20s) → Template Detection → Default Choice 1
  Returns True if successful, False otherwise
  """
  if not state.is_bot_running:
    return False

  print(f"[EVENT] Attempting to select choice {choice_index} - DATABASE-FIRST METHOD")
  
  num_choices = None
  position_mapping = None
  
  # STEP 1: Try database first (TOP PRIORITY)
  if event_text and event_type:
    print(f"[EVENT] 🔍 Checking database for event choices...")
    db_choices = state.get_event_choices_from_database(event_text, event_type)
    if db_choices and len(db_choices) > 1:
      num_choices = len(db_choices)
      print(f"[EVENT] ✅ DATABASE SUCCESS: Found {num_choices} choices - using database count")
      
      # Check if this is a learned event with a previous choice
      learned_choice = state.get_learned_choice_for_event(event_text)
      if learned_choice:
        print(f"[EVENT] 🎓 LEARNED EVENT: Using previous choice {learned_choice} directly")
        choice_index = learned_choice  # Override with learned choice
        # Skip learning mode and go directly to clicking
        num_choices = len(db_choices)  # We have the choice count
        position_mapping = None  # Will be set later
      else:
        print(f"[EVENT] 📊 Database event without learned choice - need user decision")
    else:
      print(f"[EVENT] ❌ DATABASE EMPTY: No choice data for this event")
  else:
    print(f"[EVENT] ❌ NO EVENT INFO: No event text/type provided for database lookup")
  
  # STEP 2: If database failed AND no learned choice, use intelligent learning system (20 seconds)
  if not num_choices:
    print(f"[EVENT] ⚠️  DATABASE MISSING DATA - Using intelligent learning system...")
    print(f"[EVENT] 🎓 Bot will learn from your manual choice for this event")
    
    # Use the existing intelligent learning system instead of simple wait
    try:
      # Import learning functions from state
      try:
        pre_event_stats = state.get_current_stats()
        pre_event_mood = state.get_current_mood()
        pre_event_year = state.get_current_year()
        current_support_cards = state.get_current_support_cards()
      except:
        # Fallback values if detection fails
        pre_event_stats = {}
        pre_event_mood = "Normal" 
        pre_event_year = "1st"
        current_support_cards = []
      
      # Wait for user intervention using existing learning system
      user_choice = state.wait_for_user_intervention(20)
      
      if user_choice and user_choice != "user_intervened":
        print(f"[EVENT] ✅ User selected choice {user_choice} - recording for future learning")
        
        # Log the user's choice for learning (save to event_data.json)
        state._log_user_choice_for_learning(
          event_text, 
          user_choice, 
          event_type, 
          pre_event_stats, 
          pre_event_mood, 
          pre_event_year, 
          current_support_cards
        )
        
        print(f"[EVENT] 🎓 Event learned! Next time '{event_text}' appears, bot will use choice {user_choice}")
        return True  # User already clicked, no need for bot to click
        
      elif user_choice == "user_intervened":
        print(f"[EVENT] ✅ User handled the event manually - learning system activated")
        # Try to detect which choice was made, but user already clicked
        return True
        
      else:
        print(f"[EVENT] ⏰ No user intervention - proceeding with template detection fallback")
        
    except Exception as e:
      print(f"[EVENT] ❌ Learning system error: {e} - falling back to simple wait")
      
      # Simple fallback if learning system fails
      for i in range(20, 0, -1):
        print(f"[EVENT] ⏰ Auto-fallback in {i} seconds... (manually click choice or wait)")
        time.sleep(1)
      print(f"[EVENT] ⏰ 20-second wait complete - proceeding with template detection fallback")
  
  # STEP 3: Template detection fallback (if database failed and user didn't intervene)
  if not num_choices:
    print(f"[EVENT] 🔍 Attempting template matching as fallback...")
    from core.execute import detect_number_of_choices
    num_choices, position_mapping = detect_number_of_choices()
    
    if num_choices and num_choices > 1:
      print(f"[EVENT] ✅ TEMPLATE SUCCESS: Detected {num_choices} choices")
    else:
      print(f"[EVENT] ❌ TEMPLATE FAILED: ({num_choices} choices detected)")
      print(f"[EVENT] 🚨 EMERGENCY FALLBACK: Defaulting to choice 1 click")
      num_choices = 1
      choice_index = 1  # Force choice 1 as safe fallback
  
  # STEP 4: Use coordinate-based clicking
  from core.execute import get_choice_position_by_coordinate
  choice_location = get_choice_position_by_coordinate(choice_index, num_choices, position_mapping)

  if choice_location and is_valid_mouse_position(choice_location):
    print(f"[EVENT] 🎯 Clicking choice {choice_index} at {choice_location} (based on {num_choices} total choices)")
    pyautogui.moveTo(choice_location, duration=0.2)
    pyautogui.click()
    print(f"[EVENT] ✅ Successfully selected choice {choice_index}")
    time.sleep(0.5)
    return True
  else:
    print(f"[EVENT] ❌ Failed to get valid position for choice {choice_index}")

  # STEP 5: Final template matching fallback (last resort)
  print(f"[EVENT] 🔍 Coordinate method failed, trying template fallback for choice {choice_index}")

  icon_map = {
    1: "assets/icons/event_choice_1.png",
    2: "assets/icons/event_choice_2.png",
    3: "assets/icons/event_choice_3.png",
    4: "assets/icons/event_choice_4.png",
    5: "assets/icons/event_choice_5.png"
  }

  if choice_index not in icon_map:
    print(f"[ERROR] Invalid choice index: {choice_index} (must be 1-5)")
    return False

  icon_path = icon_map[choice_index]

  # Try template matching with validation
  for attempt in range(2):
    try:
      location = pyautogui.locateCenterOnScreen(icon_path, confidence=0.8, minSearchTime=1)
      if location and is_valid_mouse_position(location):
        # Validate position makes sense
        x, y = location
        if 200 <= x <= 1000 and 300 <= y <= 900:  # Reasonable choice area
          print(f"[EVENT] ✅ Template fallback: found choice {choice_index} at {location}")
          pyautogui.moveTo(location, duration=0.2)
          pyautogui.click()
          print(f"[EVENT] ✅ Successfully selected choice {choice_index} using template fallback")
          time.sleep(0.5)
          return True
        else:
          print(f"[WARNING] Template match at {location} is outside expected choice area")
    except:
      pass

    time.sleep(0.2)


  """
  Display detailed information about event choices including stat effects
  """
  try:
    print(f"\n{'='*70}")
    print(f"📋 EVENT CHOICE DETAILS")
    print(f"{'='*70}")
    print(f"📝 Event: {event_text[:80]}...")
    print(f"🏷️  Type: {event_type}")
    
    # First check learned events for historical data
    learned_data = get_learned_event_data(event_text)
    if learned_data:
      print(f"\n🎓 LEARNED EVENT - You chose choice {learned_data.get('choice_made', '?')} before")
      outcome = learned_data.get('outcome', {})
      stat_gains = outcome.get('stat_gains', {})
      
      if stat_gains:
        print(f"📊 Previous outcome for choice {learned_data.get('choice_made', '?')}:")
        for stat, value in stat_gains.items():
          if isinstance(value, (int, float)) and value != 0:
            sign = "+" if value > 0 else ""
            # Clean up stat names
            clean_stat = stat.replace('choice_1_', '').replace('choice_2_', '').replace('choice_3_', '').replace('choice_4_', '').replace('choice_5_', '')
            if clean_stat != stat:  # Only show if it was a choice-specific stat
              print(f"   💎 {clean_stat.title()}: {sign}{value}")
      else:
        print(f"   📊 No stat data recorded for previous choice")
    
    # Try to get choices from database 
    choices = state.get_event_choices_from_database(event_text, event_type)
    
    if choices and len(choices) > 0:
      if not learned_data:  # Only show this header if we didn't show learned data
        print(f"\n✅ Found {len(choices)} choices in database:")
      else:
        print(f"\n📚 Available choices ({len(choices)} total):")
      
      # Get the full event data to extract effects
      event_data = get_full_event_data(event_text, event_type)
      
      # If we have learned data, predict stats for all choices based on the pattern
      if learned_data and event_data:
        predict_choice_effects_from_learned(learned_data, len(choices))
      
      for i, choice_text in enumerate(choices):
        choice_num = i + 1
        print(f"\n🎯 CHOICE {choice_num}: {choice_text[:60]}...")
        
        # Get effects for this choice
        effects = get_choice_effects(event_data, choice_num, event_type)
        if effects:
          for effect_type, value in effects.items():
            if isinstance(value, (int, float)) and value != 0:
              sign = "+" if value > 0 else ""
              print(f"   📊 {effect_type.title()}: {sign}{value}")
        else:
          # Check if we have learned data to predict this choice's effects
          if learned_data:
            predicted_effects = predict_choice_effect_from_pattern(learned_data, choice_num)
            if predicted_effects:
              print(f"   🔮 Predicted effects:")
              for stat, value in predicted_effects.items():
                if isinstance(value, (int, float)) and value != 0:
                  sign = "+" if value > 0 else ""
                  print(f"      📊 {stat.title()}: {sign}{value}")
            else:
              print(f"   ❓ Effects unknown")
          else:
            print(f"   ❓ Effects unknown")
    
    else:
      if not learned_data:
        print(f"\n❓ Event not found in database - LEARNING OPPORTUNITY!")
        print(f"   👤 You will have 20 seconds to manually choose")
        print(f"   🎓 Your choice will be saved for future reference")
    
    print(f"{'='*70}\n")
    
  except Exception as e:
    print(f"[ERROR] Failed to display choice details: {e}")

def predict_choice_effects_from_learned(learned_data, total_choices):
  """
  Predict effects for all choices based on learned data pattern
  """
  try:
    stat_gains = learned_data.get('outcome', {}).get('stat_gains', {})
    if not stat_gains:
      return
    
    print(f"\n🔮 PREDICTED EFFECTS (based on your previous choice):")
    
    # Group stats by choice number
    choice_stats = {}
    for key, value in stat_gains.items():
      if 'choice_' in key and isinstance(value, (int, float)) and value != 0:
        choice_num = key.split('choice_')[1].split('_')[0]
        stat_name = key.replace(f'choice_{choice_num}_', '')
        
        if choice_num not in choice_stats:
          choice_stats[choice_num] = {}
        choice_stats[choice_num][stat_name] = value
    
    for choice_num in sorted(choice_stats.keys()):
      print(f"   Choice {choice_num} predicted:")
      for stat, value in choice_stats[choice_num].items():
        sign = "+" if value > 0 else ""
        print(f"      📊 {stat.title()}: {sign}{value}")
        
  except Exception as e:
    print(f"[DEBUG] Error predicting choice effects: {e}")

def predict_choice_effect_from_pattern(learned_data, choice_num):
  """
  Predict effects for a specific choice based on learned pattern
  """
  try:
    stat_gains = learned_data.get('outcome', {}).get('stat_gains', {})
    predicted = {}
    
    choice_key = f'choice_{choice_num}_'
    for key, value in stat_gains.items():
      if key.startswith(choice_key) and isinstance(value, (int, float)) and value != 0:
        stat_name = key.replace(choice_key, '')
        predicted[stat_name] = value
    
    return predicted
  except:
    return {}

def display_event_choice_details(event_text, event_type):
  """
  Display detailed information about event choices including stat effects
  """
  try:
    print(f"\n{'='*70}")
    print(f"📋 EVENT CHOICE DETAILS")
    print(f"{'='*70}")
    print(f"📝 Event: {event_text[:80]}...")
    print(f"🏷️  Type: {event_type}")
    
    # First check learned events for historical data
    learned_data = get_learned_event_data(event_text)
    if learned_data:
      print(f"\n🎓 LEARNED EVENT - You chose choice {learned_data.get('choice_made', '?')} before")
      outcome = learned_data.get('outcome', {})
      stat_gains = outcome.get('stat_gains', {})
      
      if stat_gains:
        print(f"📊 Previous outcome for choice {learned_data.get('choice_made', '?')}:")
        for stat, value in stat_gains.items():
          if isinstance(value, (int, float)) and value != 0:
            sign = "+" if value > 0 else ""
            # Clean up stat names
            clean_stat = stat.replace('choice_1_', '').replace('choice_2_', '').replace('choice_3_', '').replace('choice_4_', '').replace('choice_5_', '')
            if clean_stat != stat:  # Only show if it was a choice-specific stat
              print(f"   💎 {clean_stat.title()}: {sign}{value}")
      else:
        print(f"   📊 No stat data recorded for previous choice")
    
    # Try to get choices from database 
    choices = state.get_event_choices_from_database(event_text, event_type)
    
    if choices and len(choices) > 0:
      if not learned_data:  # Only show this header if we didn't show learned data
        print(f"\n✅ Found {len(choices)} choices in database:")
      else:
        print(f"\n📚 Available choices ({len(choices)} total):")
      
      # Get the full event data to extract effects
      event_data = get_full_event_data(event_text, event_type)
      
      # If we have learned data, predict stats for all choices based on the pattern
      if learned_data and event_data:
        predict_choice_effects_from_learned(learned_data, len(choices))
      
      for i, choice_text in enumerate(choices):
        choice_num = i + 1
        print(f"\n🎯 CHOICE {choice_num}: {choice_text[:60]}...")
        
        # Get effects for this choice
        effects = get_choice_effects(event_data, choice_num, event_type)
        if effects:
          for effect_type, value in effects.items():
            if isinstance(value, (int, float)) and value != 0:
              sign = "+" if value > 0 else ""
              print(f"   📊 {effect_type.title()}: {sign}{value}")
        else:
          # Check if we have learned data to predict this choice's effects
          if learned_data:
            predicted_effects = predict_choice_effect_from_pattern(learned_data, choice_num)
            if predicted_effects:
              print(f"   🔮 Predicted effects:")
              for stat, value in predicted_effects.items():
                if isinstance(value, (int, float)) and value != 0:
                  sign = "+" if value > 0 else ""
                  print(f"      📊 {stat.title()}: {sign}{value}")
            else:
              print(f"   ❓ Effects unknown")
          else:
            print(f"   ❓ Effects unknown")
    
    else:
      if not learned_data:
        print(f"\n❓ Event not found in database - LEARNING OPPORTUNITY!")
        print(f"   👤 You will have 20 seconds to manually choose")
        print(f"   🎓 Your choice will be saved for future reference")
    
    print(f"{'='*70}\n")
    
  except Exception as e:
    print(f"[ERROR] Failed to display choice details: {e}")

def get_full_event_data(event_text, event_type):
  """Get full event data from database files"""
  try:
    # Import here to access database functions
    import core.state as state
    
    # Use the database lookup to get full event data
    db_data = state.get_event_choices_from_database(event_text, event_type, return_full_data=True)
    return db_data
  except Exception as e:
    print(f"[DEBUG] get_full_event_data error: {e}")
    return None

def get_choice_effects(event_data, choice_num, event_type):
  """Extract effects for a specific choice from event data"""
  try:
    if not event_data:
      return None
      
    choice_key = f"choice_{choice_num}"
    if isinstance(event_data, dict) and choice_key in event_data:
      choice_data = event_data[choice_key]
      
      # Look for effect patterns
      effects = {}
      
      if isinstance(choice_data, dict):
        # Extract stat effects - look for common stat names
        stat_keys = ['speed', 'stamina', 'power', 'guts', 'wisdom', 'skill_points', 'hp', 'motivation']
        for stat in stat_keys:
          if stat in choice_data and isinstance(choice_data[stat], (int, float)):
            effects[stat] = choice_data[stat]
            
        # Also check for effect descriptions or other numeric values
        for key, value in choice_data.items():
          if isinstance(value, (int, float)) and value != 0 and key not in stat_keys:
            effects[key] = value
            
      return effects if effects else None
      
  except Exception as e:
    print(f"[DEBUG] get_choice_effects error: {e}")
    return None

def predict_choice_effects_from_learned(learned_data, total_choices):
  """Predict effects for all choices based on learned pattern"""
  try:
    if not learned_data or 'outcome' not in learned_data:
      return
      
    chosen_choice = learned_data.get('choice_made')
    if not chosen_choice:
      return
      
    outcome = learned_data['outcome']
    stat_gains = outcome.get('stat_gains', {})
    
    if not stat_gains:
      return
      
    print(f"\n🧠 Smart Predictions based on your previous choice:")
    print(f"   📊 Your choice {chosen_choice} gave these stats:")
    
    for stat, value in stat_gains.items():
      if isinstance(value, (int, float)) and value != 0:
        sign = "+" if value > 0 else ""
        clean_stat = stat.replace(f'choice_{chosen_choice}_', '').replace('choice_made_', '')
        print(f"      💎 {clean_stat.title()}: {sign}{value}")
        
    # Give general guidance
    if total_choices > 1:
      print(f"   🎯 Other choices ({', '.join([str(i) for i in range(1, total_choices+1) if i != int(chosen_choice)])}) may have different effects")
      
  except Exception as e:
    print(f"[DEBUG] predict_choice_effects_from_learned error: {e}")

def predict_choice_effect_from_pattern(learned_data, choice_num):
  """Predict effects for a specific choice based on learned patterns"""
  try:
    if not learned_data or 'outcome' not in learned_data:
      return None
      
    chosen_choice = learned_data.get('choice_made')
    if not chosen_choice or int(chosen_choice) == choice_num:
      return None  # We already know this one
      
    # For now, just return None since we don't have data for other choices
    # In a more sophisticated system, we could analyze patterns across similar events
    return None
    
  except Exception as e:
    print(f"[DEBUG] predict_choice_effect_from_pattern error: {e}")
    return None

def get_learned_event_data(event_text):
  """Get learned data for an event"""
  try:
    # Import here to avoid circular imports
    import core.state as state
    
    # Check if we have learned data for this event using the existing function
    data = state._load_event_data_from_json()
    events = data.get("events", [])
    
    for event in events:
      if state.calculate_text_similarity(event.get('event_text', ''), event_text) > 0.8:
        return event
        
    return None
    
  except Exception as e:
    print(f"[DEBUG] get_learned_event_data error: {e}")
    return None
  """
  Get full event data from database for effect extraction
  """
  try:
    event_type_found, event_data, confidence = state.find_best_event_match(event_text)
    if event_data and confidence > 0.2:
      return event_data
    return None
  except:
    return None

def get_choice_effects(event_data, choice_num, event_type):
  """
  Extract effects for a specific choice from event data
  """
  try:
    if not event_data:
      return {}
    
    effects = {}
    
    if event_type == "character":
      choices = event_data.get("choices", [])
      if choice_num <= len(choices):
        choice = choices[choice_num - 1]
        if isinstance(choice, dict):
          # Parse effects from choice data
          choice_effects = choice.get("effects", {})
          if isinstance(choice_effects, str):
            # Parse string format like "Speed +20"
            effects.update(parse_effect_string(choice_effects))
          elif isinstance(choice_effects, dict):
            effects.update(choice_effects)
    
    elif event_type == "support":
      options = event_data.get("options", [])
      if choice_num <= len(options):
        option = options[choice_num - 1]
        if isinstance(option, dict):
          option_effects = option.get("effects", {})
          if isinstance(option_effects, str):
            effects.update(parse_effect_string(option_effects))
          elif isinstance(option_effects, dict):
            effects.update(option_effects)
    
    elif event_type == "scenario":
      choices = event_data.get("choices", [])
      if choice_num <= len(choices):
        choice = choices[choice_num - 1]
        if isinstance(choice, dict):
          # Scenario format might be different
          choice_effects = choice.get("effects", [])
          if isinstance(choice_effects, list):
            for effect in choice_effects:
              if isinstance(effect, str):
                effects.update(parse_effect_string(effect))
    
    return effects
    
  except Exception as e:
    print(f"[DEBUG] Error extracting choice effects: {e}")
    return {}

def parse_effect_string(effect_str):
  """
  Parse effect strings like "Speed +20", "Energy -10 Mood +1"
  """
  effects = {}
  try:
    import re
    # Match patterns like "Speed +20", "Power -5", etc.
    matches = re.findall(r'([A-Za-z]+)\s*([+-]?\d+)', effect_str)
    for stat, value in matches:
      effects[stat.lower()] = int(value)
  except:
    pass
  return effects

def get_learned_event_data(event_text):
  """
  Get data from previously learned events
  """
  try:
    data = state._load_event_data_from_json()
    events = data.get("events", [])
    
    for event in events:
      stored_event_text = event.get('event_text', '')
      if stored_event_text and state._events_are_similar(event_text, stored_event_text):
        return event
    
    return None
  except:
    return None

def detect_event_on_screen():
  """
  Detect if there's an actual event on screen by looking for event choice icons
  with improved filtering to avoid false positives
  Returns True if a real event is detected, False otherwise
  """
  print("[DEBUG] detect_event_on_screen() called at start")
  global last_event_detection_time, event_detection_count, last_minute_start

  # Check cooldown to prevent rapid re-detection
  current_time = time.time()
  if current_time - last_event_detection_time < EVENT_DETECTION_COOLDOWN:
    return False

  # Rate limiting: max 5 event detections per minute to prevent loops
  if current_time - last_minute_start > 60:
    last_minute_start = current_time
    event_detection_count = 0

  if event_detection_count >= 5:
    print("[EVENT] Rate limit exceeded - too many event detections in short time")
    last_event_detection_time = current_time  # Apply cooldown
    return False

  # FIRST CHECK: If next button is visible, this is definitely NOT an event
  try:
    next_buttons = [
      "assets/buttons/next_btn.png",
      "assets/buttons/next2_btn.png"
    ]
    
    for next_btn in next_buttons:
      result = pyautogui.locateCenterOnScreen(next_btn, confidence=0.6, minSearchTime=0.5)
      if result:
        print(f"[EVENT] Next button detected ({next_btn}) - this is NOT an event")
        last_event_detection_time = current_time  # Apply cooldown
        return False
  except Exception as e:
    print(f"[EVENT] Error checking for next buttons: {e}")

  # Don't detect events during race day to avoid false positives
  turn = check_turn()
  if turn == "Race Day":
    last_event_detection_time = current_time  # Apply cooldown
    return False

  # Don't detect events if we're in the middle of race processing
  year = check_current_year()
  if "Race" in year or "Finale" in year:
    last_event_detection_time = current_time  # Apply cooldown
    return False

  # Additional check: don't detect events if we're on race results screen
  print("[DEBUG] Checking for race results screen...")
  time.sleep(0.2)  # Small delay to ensure screen is fully loaded
  if is_race_results_screen():
    print("[EVENT] Race results screen detected - not an event")
    last_event_detection_time = current_time  # Apply cooldown
    return False

  # Additional check: don't detect events if we're on post-race navigation screen
  print("[DEBUG] Checking for post-race navigation screen...")
  if is_post_race_navigation_screen():
    print("[EVENT] Post-race navigation screen detected - not an event")
    last_event_detection_time = current_time  # Apply cooldown
    return False

  event_icons = [
    "assets/icons/event_choice_1.png",
    "assets/icons/event_choice_2.png",
    "assets/icons/event_choice_3.png",
    "assets/icons/event_choice_4.png",
    "assets/icons/event_choice_5.png"
  ]

  found_icons = []
  print(f"[DEBUG] Starting event choice detection - looking for {len(event_icons)} icon types")
  for icon in event_icons:
    try:
      btn = pyautogui.locateCenterOnScreen(icon, confidence=0.8, minSearchTime=0.5)
      if btn:
        # Validate position - event choices should be in the right side of screen
        if btn.x > 1500:  # Event choices are typically on the right side
          found_icons.append((icon, btn))
          print(f"[EVENT] Found potential event choice: {icon} at {btn}")
        else:
          print(f"[DEBUG] Found {icon} but at wrong position: {btn}")
    except Exception as e:
      continue

  print(f"[DEBUG] Event choice detection complete - found {len(found_icons)} valid icons")

  # Require at least 2 event choices to be present for a real event
  # (most events show multiple choices, single icons are usually UI elements)
  if len(found_icons) >= 2:
    print(f"[EVENT] Confirmed real event with {len(found_icons)} choices detected")

    # Additional validation: check if event choices are properly spaced (not decorative elements)
    if len(found_icons) > 10:
      print(f"[EVENT] Too many event choices detected ({len(found_icons)}) - checking if it's a post-race event")
      # For post-race scenarios, be more permissive
      turn = check_turn()
      if turn == "Race Day" or "Race" in str(turn):
        print(f"[EVENT] Allowing post-race event with {len(found_icons)} choices")
      else:
        last_event_detection_time = current_time  # Apply cooldown
        return False

    # Additional validation: check if there's valid event text
    try:
      quick_text_check = state.detect_event_text()
      if not quick_text_check:
        print("[EVENT] Choice icons found but no valid event text - checking post-race context")
        # For post-race, be more permissive even without text
        turn = check_turn()
        if turn == "Race Day" or "Race" in str(turn):
          print("[EVENT] Allowing post-race event without text validation")
        else:
          last_event_detection_time = current_time  # Brief cooldown
          return False
    except Exception as e:
      print(f"[EVENT] Error during text validation: {e}")
      last_event_detection_time = current_time  # Brief cooldown
      return False

    last_event_detection_time = current_time  # Update cooldown timestamp
    event_detection_count += 1  # Increment detection count
    return True
  elif len(found_icons) == 1:
    print(f"[EVENT] Only 1 choice found - likely UI element, not an event")
    # Brief cooldown for false positives to prevent rapid re-detection
    last_event_detection_time = current_time
    return False
  else:
    print(f"[DEBUG] No event choices found")
    return False

def career_lobby():
  # Program start
  print("[DEBUG] career_lobby() started - simplified version")

  # Define templates for multi-template matching
  templates = {
    "event": "assets/icons/event_choice_1.png",
    "tazuna": "assets/ui/tazuna_hint.png",
    "infirmary": "assets/buttons/infirmary_btn.png",
    "cancel": "assets/buttons/cancel_btn.png",
    "retry": "assets/buttons/retry_btn.png",
    "next": "assets/buttons/next_btn.png",
    "inspiration": "assets/buttons/inspiration_btn.png"
  }

  while state.is_bot_running:
    screen = ImageGrab.grab()
    matches = multi_match_templates(templates, screen=screen)

    print(f"[DEBUG] Template matches: {[k for k, v in matches.items() if v]}")

    # Debug: Show coordinates for all found event templates
    for key in ['event', 'event1', 'event2', 'event3', 'event4', 'event5']:
      if matches.get(key) and len(matches[key]) > 0:
        for i, box in enumerate(matches[key]):
          x, y, w, h = box
          center_x, center_y = x + w//2, y + h//2
          print(f"[DEBUG] {key} template {i+1}: center at ({center_x}, {center_y}) - box: {box}")

    # Handle events first - this is the priority
    if matches.get("event"):
      print(f"[DEBUG] Event detected - extracting event text for intelligent choice")

      # Extract event text from specified coordinates - SPLIT INTO TWO REGIONS
      try:
        # TOP region: Event type indicator (Trainee Event, Main Scenario Event, Support Card Event)
        event_type_region = (150, 157, 634-150, 190-157)  # (x, y, width, height)
        event_type_screenshot = pyautogui.screenshot(region=event_type_region)
        event_type_text = extract_text(event_type_screenshot).strip()
        
        # BOTTOM region: Actual event title
        event_title_region = (150, 190, 634-150, 241-190)  # (x, y, width, height)  
        event_title_screenshot = pyautogui.screenshot(region=event_title_region)
        event_title_text = extract_text(event_title_screenshot).strip()
        
        print(f"[EVENT] Event type: '{event_type_text}'")
        print(f"[EVENT] Event title: '{event_title_text}'")

        if event_title_text.strip():
          # Use the clean event title directly (no more messy combined text!)
          event_text = event_title_text
          print(f"[EVENT] Using clean event title: '{event_text}'")

          # Determine event type from the top region text
          event_type = "character"  # default
          if event_type_text:
            if "trainee" in event_type_text.lower():
              event_type = "character"
            elif "support" in event_type_text.lower():
              event_type = "support"  
            elif "scenario" in event_type_text.lower():
              event_type = "scenario"
          
          print(f"[EVENT] Detected event type: {event_type}")

          # Clean up event text for better matching (minimal cleaning needed now)
          cleaned_event_text = event_text.strip()
          
          # Remove trailing dots/ellipsis and normalize basic characters
          cleaned_event_text = cleaned_event_text.replace("'$", "'s").replace("' ", "'").strip()
          cleaned_event_text = cleaned_event_text.rstrip('.').strip()

          # Use DATABASE-FIRST approach with intelligent learning system
          print(f"[EVENT] Using database-first intelligent choice system...")
          
          # Check for auto-choice events first (e.g., Victory events)
          event_type_found, event_data, confidence = state.find_best_event_match(cleaned_event_text)
          if event_data and isinstance(event_data, dict) and event_data.get("auto_choice"):
            auto_choice = event_data.get("auto_choice")
            print(f"[EVENT] 🎯 AUTO-CHOICE EVENT: '{cleaned_event_text}' -> using choice {auto_choice}")
            success = select_event_choice(auto_choice, cleaned_event_text, event_type)
            if success:
              print(f"[INFO] Event handled successfully using auto-choice.")
              time.sleep(0.5)
              continue
          
          # Display choice details before making decision
          display_event_choice_details(cleaned_event_text, event_type)
          
          # Let select_event_choice handle everything: database → learning → template → fallback
          # But first determine the optimal choice if database has info
          db_choices = state.get_event_choices_from_database(cleaned_event_text, event_type)
          if db_choices and len(db_choices) > 1:
            # Database has choices, get optimal choice
            optimal_choice_tuple = state.get_optimal_event_choice_from_database(cleaned_event_text, event_type)
            optimal_choice, from_database = optimal_choice_tuple
            print(f"[EVENT] Database suggests choice {optimal_choice} for '{cleaned_event_text[:50]}...'")
          else:
            # No database info, let learning system decide
            optimal_choice = 1  # Default, but learning system will handle this
            print(f"[EVENT] No database info for '{cleaned_event_text[:50]}...', using learning system")
          
          success = select_event_choice(optimal_choice, cleaned_event_text, event_type)
          
          if success:
            print(f"[INFO] Event handled successfully using database-first approach.")
            time.sleep(0.5)
            continue
          else:
            print(f"[EVENT] Database-first approach failed, using emergency fallback...")
            # Emergency fallback - just click the first detected choice
            if click(boxes=matches["event"], text="[INFO] Event found, selecting choice 1 (emergency fallback)."):
              time.sleep(0.5)
              continue
        else:
          print("[EVENT] No text extracted from event region, using emergency fallback")
          if click(boxes=matches["event"], text="[INFO] Event found, selecting choice 1."):
            time.sleep(0.5)
            continue

      except Exception as e:
        print(f"[EVENT] Error during intelligent event processing: {e}")
        # Fall back to choice 1
        if click(boxes=matches["event"], text="[INFO] Event found, selecting choice 1 (fallback)."):
          time.sleep(0.5)
          continue

    # Handle inspiration
    if click(boxes=matches["inspiration"], text="[INFO] Inspiration found."):
      continue

    # Handle next buttons
    if click(boxes=matches["next"]):
      print("[INFO] Next button clicked")
      time.sleep(0.3)
      continue

    # Handle other buttons
    if click(boxes=matches["cancel"]):
      continue
    if click(boxes=matches["retry"]):
      continue

    # Check if we're in career lobby
    if not matches.get("tazuna"):
      print("[DEBUG] Tazuna not found - not in career lobby")
      print(".", end="")
      continue
    else:
      print("[DEBUG] Tazuna found - in career lobby")
      consecutive_next_clicks = 0  # Reset counter when in career lobby

    # Career lobby logic starts here
    if matches.get("infirmary"):
      if is_btn_active(matches["infirmary"][0]):
        # Energy-aware infirmary decision
        if state.ENERGY_DETECTION_ENABLED and state.SKIP_INFIRMARY_UNLESS_MISSING_ENERGY:
          energy_level = get_current_energy_level()
          if energy_level > state.SKIP_TRAINING_ENERGY:
            print(f"[INFO] Character debuffed, but energy is sufficient ({energy_level}% > {state.SKIP_TRAINING_ENERGY}%). Skipping infirmary.")
          else:
            click(boxes=matches["infirmary"][0], text="[INFO] Character debuffed and energy low, going to infirmary.")
            continue
        else:
          click(boxes=matches["infirmary"][0], text="[INFO] Character debuffed, going to infirmary.")
          continue

    mood = check_mood()
    mood_index = MOOD_LIST.index(mood)
    minimum_mood = MOOD_LIST.index(state.MINIMUM_MOOD)
    turn = check_turn()
    year = check_current_year()
    criteria = check_criteria()
    year_parts = year.split(" ")
    
    # Check energy level if detection is enabled
    energy_info = ""
    if state.ENERGY_DETECTION_ENABLED:
      energy_level, energy_numeric = check_energy()
      energy_info = f"Energy: {energy_level} ({energy_numeric}%)"

    print("\n=======================================================================================\n")
    print(f"Year: {year}")
    print(f"Mood: {mood}")
    if energy_info:
      print(f"{energy_info}")
    print(f"Turn: {turn}\n")

    # URA SCENARIO
    if year == "Finale Season" and turn == "Race Day":
      print("[INFO] URA Finale")
      if state.IS_AUTO_BUY_SKILL:
        auto_buy_skill()
      ura()
      for i in range(2):
        if click(img="assets/buttons/race_btn.png", minSearch=2):
          time.sleep(0.5)

      race_prep()
      time.sleep(1)
      after_race()
      continue

    # If calendar is race day, do race
    if turn == "Race Day" and year != "Finale Season":
      print("[INFO] Race Day.")
      if state.IS_AUTO_BUY_SKILL and year_parts[0] != "Junior":
        auto_buy_skill()
      race_day()
      continue

    # Mood check
    if mood_index < minimum_mood:
      print("[INFO] Mood is low, trying recreation to increase mood")
      do_recreation()
      continue

    # Check if goals is not met criteria AND it is not Pre-Debut AND turn is less than 10 AND Goal is already achieved
    if criteria.split(" ")[0] != "criteria" and year != "Junior Year Pre-Debut" and turn < 10 and criteria != "Goal Achievedl":
      race_found = do_race()
      if race_found:
        continue
      else:
        # If there is no race matching to aptitude, go back and do training instead
        click(img="assets/buttons/back_btn.png", minSearch=1, text="[INFO] Race not found. Proceeding to training.")
        time.sleep(0.5)

    # If Prioritize G1 Race is true, check G1 race every turn
    if state.PRIORITIZE_G1_RACE and year_parts[0] != "Junior" and len(year_parts) > 3 and year_parts[3] not in ["Jul", "Aug"]:
      g1_race_found = do_race(state.PRIORITIZE_G1_RACE)
      if g1_race_found:
        continue
      else:
        # If there is no G1 race, go back and do training
        click(img="assets/buttons/back_btn.png", minSearch=1, text="[INFO] G1 race not found. Proceeding to training.")
        time.sleep(0.5)

    # Check training button
    if not go_to_training():
      print("[INFO] Training button is not found.")
      continue

    # Last, do training
    time.sleep(0.5)
    results_training = check_training()

    best_training = do_something(results_training)
    if best_training:
      go_to_training()
      time.sleep(0.5)
      do_train(best_training)
    else:
      do_rest()
    time.sleep(1)
