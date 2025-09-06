import cv2
import numpy as np
from PIL import ImageGrab, ImageStat

from utils.screenshot import capture_region

def match_template(template_path, region=None, threshold=0.85):
  # Get screenshot
  if region:
    screen = np.array(ImageGrab.grab(bbox=region))  # (left, top, right, bottom)
  else:
    screen = np.array(ImageGrab.grab())
  screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

  # Load template
  template = cv2.imread(template_path, cv2.IMREAD_COLOR)  # safe default
  if template.shape[2] == 4:
    template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)
  result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
  loc = np.where(result >= threshold)

  h, w = template.shape[:2]
  boxes = [(x, y, w, h) for (x, y) in zip(*loc[::-1])]

  return deduplicate_boxes(boxes)

def multi_match_templates(templates, screen=None, threshold=0.85):
  if screen is None:
    screen = ImageGrab.grab()
  screen_bgr = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

  results = {}
  for name, path in templates.items():
    template = cv2.imread(path, cv2.IMREAD_COLOR)
    if template is None:
      results[name] = []
      continue
    if template.shape[2] == 4:
      template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    h, w = template.shape[:2]
    boxes = [(x, y, w, h) for (x, y) in zip(*loc[::-1])]
    results[name] = boxes
  return results

def deduplicate_boxes(boxes, min_dist=5):
  filtered = []
  for x, y, w, h in boxes:
    cx, cy = x + w // 2, y + h // 2
    if all(abs(cx - (fx + fw // 2)) > min_dist or abs(cy - (fy + fh // 2)) > min_dist
        for fx, fy, fw, fh in filtered):
      filtered.append((x, y, w, h))
  return filtered

def is_btn_active(region, treshold = 150):
  screenshot = capture_region(region)
  grayscale = screenshot.convert("L")
  stat = ImageStat.Stat(grayscale)
  avg_brightness = stat.mean[0]

  # Treshold btn
  return avg_brightness > treshold

def detect_energy_level_by_color(screenshot_path):
    """
    Detect energy level based on the color of the energy bar.
    
    Color progression from low to high energy:
    Blue (low) -> Aqua -> Green -> Yellow -> Orange/Red (high)
    
    Returns:
        float: Energy level from 0.0 (empty) to 1.0 (full)
    """
    try:
        # Load the screenshot
        image = cv2.imread(screenshot_path)
        if image is None:
            print(f"Could not load image: {screenshot_path}")
            return None
        
        # Convert BGR to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define energy bar region (adjust these coordinates based on your game resolution)
        # These are approximate values - you may need to adjust them
        energy_bar_region = hsv[10:30, 50:300]  # Adjust coordinates as needed
        
        # Define HSV color ranges for each energy level
        # Color progression: Blue (low) -> Aqua -> Green -> Yellow -> Orange/Red (high)
        color_ranges = {
            'blue': ([100, 50, 50], [130, 255, 255]),      # Low energy
            'aqua': ([80, 50, 50], [100, 255, 255]),       # Low-medium energy
            'green': ([40, 50, 50], [80, 255, 255]),       # Medium energy
            'yellow': ([20, 50, 50], [40, 255, 255]),      # Medium-high energy
            'orange': ([0, 50, 50], [20, 255, 255]),       # High energy (orange/red)
            'red': ([160, 50, 50], [180, 255, 255])        # Very high energy (red)
        }
        
        # Count pixels for each color
        color_counts = {}
        total_pixels = energy_bar_region.shape[0] * energy_bar_region.shape[1]
        
        for color_name, (lower, upper) in color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            mask = cv2.inRange(energy_bar_region, lower, upper)
            color_counts[color_name] = np.sum(mask > 0)
        
        # Find the dominant color
        if total_pixels == 0:
            return None
            
        dominant_color = max(color_counts, key=color_counts.get)
        dominant_percentage = color_counts[dominant_color] / total_pixels
        
        # Only consider it valid if the dominant color takes up a significant portion
        if dominant_percentage < 0.1:  # Less than 10% of the region
            return None
        
        # Map colors to energy levels (0.0 to 1.0)
        # Corrected mapping: Blue = low, Orange/Red = high
        energy_mapping = {
            'blue': 0.1,      # Low energy (10%)
            'aqua': 0.3,      # Low-medium energy (30%)
            'green': 0.5,     # Medium energy (50%)
            'yellow': 0.7,    # Medium-high energy (70%)
            'orange': 0.9,    # High energy (90%)
            'red': 1.0        # Very high energy (100%)
        }
        
        energy_level = energy_mapping.get(dominant_color, 0.5)
        print(f"Energy detection: Dominant color = {dominant_color}, Energy level = {energy_level:.1%}")
        
        return energy_level
        
    except Exception as e:
        print(f"Error in energy color detection: {e}")
        return None

def detect_energy_by_region(region):
    """
    Detect energy level by analyzing a specific screen region containing the energy bar.
    
    Args:
        region: Tuple (left, top, right, bottom) defining the energy bar area
        
    Returns:
        float: Energy level from 0.0 to 1.0, or None if detection fails
    """
    try:
        # Capture the energy bar region
        screenshot = capture_region(region)
        
        # Convert PIL image to OpenCV format
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)
        
        # Define HSV color ranges for each energy level
        # Blue (low) -> Aqua -> Green -> Yellow -> Orange/Red (high)
        color_ranges = {
            'blue': ([100, 50, 50], [130, 255, 255]),      # Low energy
            'aqua': ([80, 50, 50], [100, 255, 255]),       # Low-medium energy
            'green': ([40, 50, 50], [80, 255, 255]),       # Medium energy
            'yellow': ([20, 50, 50], [40, 255, 255]),      # Medium-high energy
            'orange': ([0, 50, 50], [20, 255, 255]),       # High energy (orange/red)
            'red': ([160, 50, 50], [180, 255, 255])        # Very high energy (red)
        }
        
        # Count pixels for each color
        color_counts = {}
        total_pixels = hsv.shape[0] * hsv.shape[1]
        
        for color_name, (lower, upper) in color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            mask = cv2.inRange(hsv, lower, upper)
            color_counts[color_name] = np.sum(mask > 0)
        
        # Find the dominant color
        if total_pixels == 0:
            return None
            
        dominant_color = max(color_counts, key=color_counts.get)
        dominant_percentage = color_counts[dominant_color] / total_pixels
        
        # Only consider it valid if the dominant color takes up a significant portion
        if dominant_percentage < 0.05:  # Less than 5% of the region
            return None
        
        # Map colors to energy levels (0.0 to 1.0)
        # Blue = low energy, Orange/Red = high energy
        energy_mapping = {
            'blue': 0.1,      # Low energy (10%)
            'aqua': 0.3,      # Low-medium energy (30%)
            'green': 0.5,     # Medium energy (50%)
            'yellow': 0.7,    # Medium-high energy (70%)
            'orange': 0.9,    # High energy (90%)
            'red': 1.0        # Very high energy (100%)
        }
        
        energy_level = energy_mapping.get(dominant_color, 0.5)
        print(f"Energy detection (region): Dominant color = {dominant_color} ({dominant_percentage:.1%}), Energy level = {energy_level:.1%}")
        
        return energy_level
        
    except Exception as e:
        print(f"Error in energy region detection: {e}")
        return None
