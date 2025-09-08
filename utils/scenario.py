import pyautogui
import time

def ura():
  """Handle URA finale race with proper button detection and race position selection"""
  try:
    # Try to find the URA race button with multiple attempts
    race_btn = None
    for attempt in range(3):
      print(f"[URA] Attempt {attempt + 1}: Looking for URA race button...")
      race_btn = pyautogui.locateCenterOnScreen("assets/ura/ura_race_btn.png", confidence=0.8, minSearchTime=2)
      if race_btn:
        print(f"[URA] Found URA race button at {race_btn}")
        pyautogui.click(race_btn)
        time.sleep(0.5)
        break
      time.sleep(0.5)
    
    if not race_btn:
      print("[URA] URA race button not found, trying fallback...")
      # Fallback: try regular race button
      regular_btn = pyautogui.locateCenterOnScreen("assets/buttons/race_btn.png", confidence=0.8, minSearchTime=2)
      if regular_btn:
        print(f"[URA] Found regular race button at {regular_btn}")
        pyautogui.click(regular_btn)
        time.sleep(0.5)
      else:
        print("[URA] No race button found at all!")
        return False
    
    # Add race position selection for URA finale
    try:
      from core.execute import select_race_position
      print("[URA] Selecting race position for URA finale...")
      select_race_position()
    except Exception as e:
      print(f"[URA] Warning: Could not select race position: {e}")
    
    # Click race button one more time to confirm
    time.sleep(0.5)
    confirm_btn = pyautogui.locateCenterOnScreen("assets/buttons/race_btn.png", confidence=0.8, minSearchTime=1)
    if confirm_btn:
      pyautogui.click(confirm_btn)
      time.sleep(0.5)
      print("[URA] Race confirmed for URA finale")
    
    return True
    
  except Exception as e:
    print(f"[URA] Error in URA finale handler: {e}")
    return False