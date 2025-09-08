import time
import pyautogui
import difflib  # Built-in Python library for string similarity

from utils.screenshot import enhanced_screenshot
from core.ocr import extract_text
from core.recognizer import match_template, is_btn_active
import core.state as state

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

def buy_skill():
  # Move to safe position first
  safe_pos = (560, 680)
  if is_valid_mouse_position(safe_pos):
    pyautogui.moveTo(x=560, y=680)
  else:
    print("[DEBUG] Safe position (560, 680) is invalid, skipping initial move")
  found = False

  for i in range(10):
    # Pause a bit at the bottom to wait until the scrolling animation ends
    if i > 8:
      time.sleep(0.5)
    buy_skill_icon = match_template("assets/icons/buy_skill.png", threshold=0.9)

    if buy_skill_icon:
      for x, y, w, h in buy_skill_icon:
        region = (x - 420, y - 40, w + 275, h + 5)
        screenshot = enhanced_screenshot(region)
        text = extract_text(screenshot)
        if is_skill_match(text, state.SKILL_LIST):
          button_region = (x, y, w, h)
          if is_btn_active(button_region):
            print(f"[INFO] Buy {text}")
            pyautogui.click(x=x + 5, y=y + 5, duration=0.15)
            found = True
          else:
            print(f"[INFO] {text} found but not enough skill points.")

    for i in range(7):
      pyautogui.scroll(-300)

  return found

def calculate_similarity(str1: str, str2: str) -> float:
  """Calculate similarity between two strings using built-in difflib (0.0 to 1.0)"""
  return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def is_skill_match(text: str, skill_list: list[str], threshold: float = 0.8) -> bool:
  """
  Enhanced skill matching that uses both the configured skill list and the comprehensive skill database
  """
  text_lower = text.lower()

  # First check against the configured skill list (original behavior)
  for skill in skill_list:
    similarity = calculate_similarity(text_lower, skill.lower())
    if similarity >= threshold:
      return True

  # If no match found, try enhanced matching with skill database
  try:
    import core.state as state
    if state.SKILL_DATA:
      for skill in state.SKILL_DATA:
        skill_name_en = skill.get('name_en', '').lower()
        skill_name_jp = skill.get('name_jp', '').lower()
        skill_desc = skill.get('description_en', '').lower()

        # Check exact matches first
        if skill_name_en == text_lower or skill_name_jp == text_lower:
          return True

        # Check partial matches
        if (skill_name_en in text_lower or
            skill_name_jp in text_lower or
            text_lower in skill_name_en or
            text_lower in skill_name_jp):
          return True

        # Check description matches (lower threshold for descriptions)
        desc_similarity = calculate_similarity(text_lower, skill_desc)
        if desc_similarity >= (threshold - 0.1):  # Slightly lower threshold for descriptions
          return True

  except Exception as e:
    # If enhanced matching fails, just continue with original logic
    pass

  return False