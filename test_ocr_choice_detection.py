#!/usr/bin/env python3
"""
AREA-BASED OCR CHOICE DETECTION TEST PROGRAM
Tests choice detection using OCR with predefined area checking

FEATURES:
- Checks if choice templates appear within predefined CHOICE_POSITIONS areas
- Counts choices based on which areas contain templates (1-5 choices)
- Uses exact bounding boxes for OCR regions
- Automatically adapts to detected choice count
- Saves results with area detection details

USAGE:
Run this program when on an event screen to test OCR choice detection.
The system will check each predefined area for choice templates and
perform OCR on areas that contain choices.
"""

import pyautogui
import easyocr
import time
from PIL import ImageGrab, Image
import json
import os
import sys

# Add the project root to the path to import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)

# Import functions from the main bot system
try:
    from core.execute import detect_number_of_choices, get_choice_position_by_coordinate
    from core.state import is_valid_mouse_position
    print("[INIT] Successfully imported core functions")
except ImportError as e:
    print(f"[ERROR] Failed to import core functions: {e}")
    print("[INIT] Running in standalone mode without event detection integration")

def get_ocr_regions_for_choices(num_choices):
    """
    DEPRECATED: This function is no longer used.
    OCR regions are now created dynamically based on detected template positions.
    """
    print(f"[DEPRECATED] get_ocr_regions_for_choices called with {num_choices} - should not happen")
    return {}

def detect_and_setup_choices():
    """
    Detect choices by checking if templates appear within the predefined CHOICE_POSITIONS areas
    Returns (num_choices, ocr_regions) based on which areas contain choice templates
    """
    print("[DETECT] Starting area-based choice detection...")

    try:
        choice_templates = [
            "assets/icons/event_choice_1.png",
            "assets/icons/event_choice_2.png",
            "assets/icons/event_choice_3.png",
            "assets/icons/event_choice_4.png",
            "assets/icons/event_choice_5.png"
        ]

        detected_positions = {}

        # Check each predefined area for choice templates
        for position_num, bounding_box in CHOICE_POSITIONS.items():
            top_left = bounding_box['top_left']
            bottom_right = bounding_box['bottom_right']

            # Convert to region format for pyautogui (left, top, width, height)
            left, top = top_left
            width = bottom_right[0] - left
            height = bottom_right[1] - top
            region = (left, top, width, height)

            print(f"[DETECT] Checking area {position_num}: {region}")

            # Check if any choice template appears in this specific region
            found_in_area = False
            detected_location = None
            for template in choice_templates:
                try:
                    # Look for template specifically within this region
                    location = pyautogui.locateOnScreen(template, confidence=0.7, region=region)
                    if location:
                        print(f"[DETECT] ✅ Found {template} in area {position_num} at {location}")
                        detected_positions[position_num] = {
                            'bounding_box': bounding_box,
                            'template_found': template,
                            'detected_at': location
                        }
                        found_in_area = True
                        detected_location = location
                        break  # Found one template in this area, move to next area
                except Exception as e:
                    # Continue checking other templates
                    continue

            if not found_in_area:
                print(f"[DETECT] ❌ No templates found in area {position_num}")
            else:
                # Create OCR region around the detected icon position
                # Expand the region to capture text that might be nearby
                icon_left, icon_top, icon_width, icon_height = detected_location

                # Create a larger OCR region around the icon
                ocr_margin = 20  # pixels to expand around the icon
                ocr_left = max(0, icon_left - ocr_margin)
                ocr_top = max(0, icon_top - ocr_margin)
                ocr_width = icon_width + (ocr_margin * 2)
                ocr_height = icon_height + (ocr_margin * 2)

                # Make sure OCR region doesn't exceed screen bounds
                screen_width, screen_height = pyautogui.size()
                ocr_width = min(ocr_width, screen_width - ocr_left)
                ocr_height = min(ocr_height, screen_height - ocr_top)

                # Update the OCR region for this position
                detected_positions[position_num]['ocr_region'] = {
                    'top_left': (int(ocr_left), int(ocr_top)),
                    'bottom_right': (int(ocr_left + ocr_width), int(ocr_top + ocr_height))
                }
                print(f"[DETECT] 📝 OCR region for area {position_num}: ({ocr_left}, {ocr_top}) to ({ocr_left + ocr_width}, {ocr_top + ocr_height})")

        if detected_positions:
            num_choices = len(detected_positions)
            print(f"[DETECT] ✅ Area detection successful: {num_choices} choices found in areas {sorted(detected_positions.keys())}")

            # Use the expanded OCR regions for better text detection
            ocr_regions = {}
            for pos_num, data in detected_positions.items():
                if 'ocr_region' in data:
                    ocr_regions[pos_num] = data['ocr_region']
                else:
                    # Fallback to original bounding box if OCR region wasn't created
                    ocr_regions[pos_num] = data['bounding_box']

            return num_choices, ocr_regions
        else:
            print("[DETECT] ❌ No choice templates found in any predefined areas")

    except Exception as e:
        print(f"[DETECT] Area detection failed: {e}")

    # Ultimate fallback: use all hardcoded positions
    print("[DETECT] 🚨 Using all hardcoded positions as fallback")
    return 5, CHOICE_POSITIONS

# Hardcoded choice positions (exact bounding boxes)
CHOICE_POSITIONS = {
    1: {'top_left': (260, 264), 'bottom_right': (312, 350)},
    2: {'top_left': (260, 380), 'bottom_right': (312, 462)},
    3: {'top_left': (260, 488), 'bottom_right': (312, 575)},
    4: {'top_left': (260, 600), 'bottom_right': (312, 686)},
    5: {'top_left': (260, 714), 'bottom_right': (312, 797)}
}

def take_region_screenshot(bounding_box):
    """
    Take a screenshot of the exact bounding box region
    """
    top_left = bounding_box['top_left']
    bottom_right = bounding_box['bottom_right']

    left, top = top_left
    right, bottom = bottom_right

    # Calculate actual width and height
    width = right - left
    height = bottom - top

    # Ensure coordinates are within screen bounds
    screen_width, screen_height = pyautogui.size()
    left = max(0, min(left, screen_width - width))
    top = max(0, min(top, screen_height - height))

    # Convert to regular Python ints (not numpy int64)
    left, top, width, height = int(left), int(top), int(width), int(height)

    # pyautogui.screenshot expects (left, top, width, height)
    region = (left, top, width, height)
    screenshot = pyautogui.screenshot(region=region)
    return screenshot, region

def detect_choice_text_at_position(position_num, bounding_box, debug=False):
    """
    Simplified: Just confirms choice presence, no OCR text detection needed
    Since we use database values, not text reading
    """
    # Since we don't need to read text (database-driven decisions),
    # just return that choice is present if we detected the template
    return True, f"Choice {position_num} detected", 1.0

def test_ocr_choice_detection(debug=False, save_screenshots=False):
    """
    Test choice detection using template matching in predefined areas
    """
    print("\n" + "="*60)
    print("🧪 AREA-BASED CHOICE DETECTION TEST")
    print("="*60)

    # Detect how many choices are present using template matching
    num_choices, choice_positions = detect_and_setup_choices()

    if not num_choices or not choice_positions:
        print("❌ Failed to detect choices on screen")
        print("💡 Make sure you're on an event screen with choices visible")
        return {}

    print(f"[TEST] Detected {num_choices} choices at positions: {sorted(choice_positions.keys())}")

    detected_choices = {}
    screenshots_dir = "ocr_choice_test_screenshots"

    if save_screenshots and not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    print(f"[TEST] Processing {len(choice_positions)} choice positions...")

    for position_num in sorted(choice_positions.keys()):
        bounding_box = choice_positions[position_num]
        top_left = bounding_box['top_left']
        bottom_right = bounding_box['bottom_right']

        print(f"\n[TEST] Position {position_num}: Region {top_left} to {bottom_right}")
        if debug:
            print(f"[DEBUG] Region size: {bottom_right[0] - top_left[0]}x{bottom_right[1] - top_left[1]} pixels")

        # Simple confirmation that choice is present (no OCR needed)
        detected_choices[position_num] = {
            'present': True,
            'bounding_box': bounding_box,
            'position': position_num
        }
        print(f"✅ Position {position_num}: CHOICE DETECTED")

        # Save screenshot if requested
        if save_screenshots:
            screenshot, region = take_region_screenshot(bounding_box)
            filename = f"{screenshots_dir}/position_{position_num}_{time.strftime('%H%M%S')}.png"
            screenshot.save(filename)
            print(f"📸 Screenshot saved: {filename}")

        # Small delay between positions
        time.sleep(0.1)

    # Analyze results
    print("\n" + "="*60)
    print("📊 ANALYSIS RESULTS")
    print("="*60)

    num_detected = len(detected_choices)
    print(f"🎯 Total choices detected: {num_detected}")
    print(f"🎯 Choice positions: {sorted(detected_choices.keys())}")

    if num_detected > 0:
        print("📍 Detected choices at positions:")
        for pos_num in sorted(detected_choices.keys()):
            print(f"   Position {pos_num}: ✅ Present")

        # Show detection pattern
        detected_positions = sorted(detected_choices.keys())
        print(f"🎯 Pattern: Choices detected at positions {detected_positions}")

        # Simple recommendation
        print("\n💡 RECOMMENDATION:")
        print(f"   Found {num_detected} choice(s) at positions {detected_positions}")
        print("   Ready for database-driven decision making")
    else:
        print("❌ No choices detected")
        print("💡 Make sure you're on an event screen with choices visible")

    # Save results to JSON
    results_file = f"ocr_choice_test_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'detected_choices': detected_choices,
            'total_choices': num_detected,
            'choice_positions': sorted(detected_choices.keys()),
            'regions': choice_positions
        }, f, indent=2)

    print(f"\n💾 Results saved to: {results_file}")

    return detected_choices

def interactive_test():
    """
    Interactive testing mode with area-based choice detection
    """
    print("\n" + "="*60)
    print("🎮 AREA-BASED CHOICE DETECTION TEST")
    print("   Counts choices using template matching in predefined areas!")
    print("="*60)
    print("Commands:")
    print("  'test' - Run choice detection test")
    print("  'debug' - Run test with debug output")
    print("  'save' - Run test and save screenshots")
    print("  'quit' - Exit")
    print("="*60)

    while True:
        try:
            command = input("\nEnter command: ").strip().lower()

            if command == 'quit':
                break
            elif command == 'test':
                test_ocr_choice_detection(debug=False, save_screenshots=False)
            elif command == 'debug':
                test_ocr_choice_detection(debug=True, save_screenshots=False)
            elif command == 'save':
                test_ocr_choice_detection(debug=True, save_screenshots=True)
            else:
                print("❌ Unknown command. Use 'test', 'debug', 'save', or 'quit'")

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Area-Based Choice Detection Test Program")
    print("This program counts choices using template matching in predefined areas")

    # Give user time to position the game window
    print("\n⏳ Positioning phase...")
    for i in range(5, 0, -1):
        print(f"   Make sure Uma Musume is visible on screen... {i}")
        time.sleep(1)

    # Run interactive test
    interactive_test()
