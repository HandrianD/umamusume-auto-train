import time
import pyautogui
import Levenshtein

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

def is_skill_match(text: str, skill_list: list[str], threshold: float = 0.8) -> bool:
  for skill in skill_list:
    similarity = Levenshtein.ratio(text.lower(), skill.lower())
    if similarity >= threshold:
      return True
  return False