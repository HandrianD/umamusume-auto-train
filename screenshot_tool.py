import pyautogui
import json
import os
import numpy as np
from datetime import datetime
from core.ocr import extract_text
from core.recognizer import match_template

# File to save coordinates
COORDS_FILE = "detected_coords.json"

def take_screenshot():
    """Take a full screenshot and return the image."""
    screenshot = pyautogui.screenshot()
    return screenshot

def detect_text_coordinates(screenshot, text_to_find):
    """Use OCR to detect text and return coordinates of the bounding box."""
    from core.ocr import extract_text  # Assuming extract_text uses easyocr
    # For better accuracy, use easyocr directly
    import easyocr
    reader = easyocr.Reader(["en"], gpu=False)
    img_np = np.array(screenshot)
    results = reader.readtext(img_np)
    
    for (bbox, text, confidence) in results:
        if text_to_find.lower() in text.lower():
            # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
            center_x = sum(x_coords) / 4
            center_y = sum(y_coords) / 4
            return {"x": int(center_x), "y": int(center_y), "bbox": bbox, "text": text, "confidence": confidence}
    return None

def detect_button_coordinates(screenshot, button_image_path):
    """Use template matching to detect button and return coordinates."""
    # The match_template function grabs the screen, so no need for temp file
    pos = match_template(button_image_path)
    if pos:
        return {"x": pos[0], "y": pos[1], "button": button_image_path}
    return None

def save_coordinates(coords, label):
    """Save coordinates to JSON file."""
    data = {}
    if os.path.exists(COORDS_FILE):
        with open(COORDS_FILE, "r") as f:
            data = json.load(f)
    
    data[label] = coords
    data["timestamp"] = datetime.now().isoformat()
    
    with open(COORDS_FILE, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Saved coordinates for {label}: {coords}")

def main():
    print("Taking screenshot...")
    screenshot = take_screenshot()
    
    # Save screenshot for debugging
    screenshot.save("debug_screenshot.png")
    print("Screenshot saved as debug_screenshot.png")
    
    # Example: Detect training button
    button_path = "assets/buttons/training_btn.png"
    if os.path.exists(button_path):
        coords = detect_button_coordinates(screenshot, button_path)
        if coords:
            save_coordinates(coords, "training_button")
        else:
            print("Button not found. Check if the game is on the training screen or adjust the image.")
    else:
        print(f"Button image not found at {button_path}")
    
    # Example: Detect text (e.g., "SPD")
    text_coords = detect_text_coordinates(screenshot, "SPD")
    if text_coords:
        save_coordinates(text_coords, "spd_text")
    else:
        print("Text 'SPD' not found. Check OCR or try different text.")

if __name__ == "__main__":
    main()
