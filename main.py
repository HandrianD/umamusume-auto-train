import time
import pygetwindow as gw
import threading
import uvicorn
import keyboard
import pyautogui

from core.execute import career_lobby
import core.state as state
from server.main import app

hotkey = "f1"

def focus_umamusume():
  try:
    print("[DEBUG] Looking for windows with title 'Umamusume'...")
    win = gw.getWindowsWithTitle("Umamusume")
    print(f"[DEBUG] Found {len(win)} windows with 'Umamusume' in title")
    for w in win:
      print(f"[DEBUG] Window: '{w.title}' - IsActive: {w.isActive} - IsMinimized: {w.isMinimized}")
    
    target_window = next((w for w in win if w.title.strip() == "Umamusume"), None)
    if target_window:
      print(f"[DEBUG] Found exact match: '{target_window.title}'")
      if target_window.isMinimized:
        print("[DEBUG] Window is minimized, restoring...")
        target_window.restore()
      else:
        print("[DEBUG] Window is not minimized, minimizing then restoring...")
        target_window.minimize()
        time.sleep(0.2)
        target_window.restore()
        time.sleep(0.5)
      print("[DEBUG] Window focus operation completed")
      return True
    else:
      print("[DEBUG] No exact match found for 'Umamusume' title")
      return False
  except Exception as e:
    print(f"Error focusing window: {e}")
    return False

def main():
  print("Uma Auto!")
  print("[DEBUG] Attempting to focus Umamusume window...")
  if focus_umamusume():
    print("[DEBUG] Window focused successfully, reloading config...")
    state.reload_config()
    print("[DEBUG] Setting bot to running state...")
    state.is_bot_running = True
    print("[DEBUG] Config reloaded, starting career_lobby...")
    career_lobby()
  else:
    print("Failed to focus Umamusume window")

def hotkey_listener():
  while True:
    keyboard.wait(hotkey)
    if not state.is_bot_running:
      print("[BOT] Starting...")
      state.is_bot_running = True
      t = threading.Thread(target=main, daemon=True)
      t.start()
    else:
      print("[BOT] Stopping...")
      state.is_bot_running = False
    time.sleep(0.5)

def start_server():
  res = pyautogui.resolution()
  if res.width != 1920 or res.height != 1080:
    print(f"[ERROR] Your resolution is {res.width} x {res.height}. Please set your screen to 1920 x 1080.")
    return
  host = "127.0.0.1"
  port = 8000
  print(f"[INFO] Press '{hotkey}' to start/stop the bot.")
  print(f"[SERVER] Open http://{host}:{port} to configure the bot.")
  config = uvicorn.Config(app, host=host, port=port, workers=1, log_level="warning")
  server = uvicorn.Server(config)
  server.run()

if __name__ == "__main__":
  threading.Thread(target=hotkey_listener, daemon=True).start()
  start_server()
