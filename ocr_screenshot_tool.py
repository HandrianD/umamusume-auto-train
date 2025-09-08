import pyautogui
import easyocr
from PIL import Image, ImageTk
import json
import os
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class RegionSelector:
    def __init__(self, screenshot):
        self.original_screenshot = screenshot  # Keep original for coordinate conversion
        self.display_screenshot = screenshot  # This might be resized for display
        self.scale_factor = 1.0  # Will be updated if resized
        
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None
        self.selected_region = None

        # Create tkinter window
        self.root = tk.Tk()
        self.root.title("Select Region for OCR")

        # Get screen size and resize screenshot if too large
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Leave some space for instructions (about 100px)
        max_width = screen_width - 50
        max_height = screen_height - 100
        
        # Check if resize is needed
        if self.display_screenshot.width > max_width or self.display_screenshot.height > max_height:
            # Calculate scaling factor
            self.scale_factor = min(max_width / self.display_screenshot.width, max_height / self.display_screenshot.height)
            new_width = int(self.display_screenshot.width * self.scale_factor)
            new_height = int(self.display_screenshot.height * self.scale_factor)
            
            # Resize for display only
            self.display_screenshot = self.display_screenshot.resize((new_width, new_height), Image.LANCZOS)
            print(f"Screenshot resized for display: {new_width}x{new_height} (scale: {self.scale_factor:.3f})")
        else:
            print("Screenshot fits screen, no resize needed")

        # Convert display PIL image to Tkinter format
        self.photo = ImageTk.PhotoImage(self.display_screenshot)

        # Create canvas with scrollbars
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.frame, width=self.display_screenshot.width, height=self.display_screenshot.height)
        
        # Add scrollbars
        self.h_scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Display image
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Bind keyboard events
        self.root.bind("<space>", lambda e: self.confirm_selection())
        self.root.bind("r", lambda e: self.reset_selection())
        self.root.bind("c", lambda e: self.root.quit())
        self.root.focus_set()  # Make sure window has focus for keyboard events

        # Instructions label
        instructions = tk.Label(self.root, text="Click & drag to select | SPACE: Confirm | R: Reset | C: Cancel", font=('Arial', 10))
        instructions.pack(pady=5)
        
        # Scale info label
        if self.scale_factor != 1.0:
            scale_info = tk.Label(self.root, text=f"Screenshot scaled to {self.scale_factor:.2f}x for display - coordinates will be converted back to original", font=('Arial', 8), fg='blue')
            scale_info.pack(pady=2)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        self.end_x = event.x
        self.end_y = event.y

    def reset_selection(self):
        """Reset the current selection"""
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        print("Selection reset")

    def confirm_selection(self):
        if self.start_x is None or self.end_x is None:
            messagebox.showerror("Error", "Please select a region first")
            return

        # Calculate region coordinates on the DISPLAY image
        display_left = min(self.start_x, self.end_x)
        display_top = min(self.start_y, self.end_y)
        display_width = abs(self.end_x - self.start_x)
        display_height = abs(self.end_y - self.start_y)

        if display_width == 0 or display_height == 0:
            messagebox.showerror("Error", "Selected region is too small")
            return

        # Convert display coordinates back to ORIGINAL screenshot coordinates
        original_left = int(display_left / self.scale_factor)
        original_top = int(display_top / self.scale_factor)
        original_width = int(display_width / self.scale_factor)
        original_height = int(display_height / self.scale_factor)

        print(f"Display region: {display_left},{display_top} {display_width}x{display_height}")
        print(f"Original region: {original_left},{original_top} {original_width}x{original_height}")
        
        self.selected_region = (original_left, original_top, original_width, original_height)
        self.root.quit()

    def run(self):
        self.root.mainloop()
        self.root.destroy()
        return self.selected_region

def take_screenshot_and_ocr():
    """
    Take a screenshot, let user select a region interactively, run OCR, and save results.
    """
    # Create output directory if it doesn't exist
    output_dir = "ocr_screenshots"
    os.makedirs(output_dir, exist_ok=True)

    # Take full screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot = pyautogui.screenshot()
    full_screenshot_path = os.path.join(output_dir, f"screenshot_{timestamp}.png")
    screenshot.save(full_screenshot_path)
    print(f"Full screenshot saved: {full_screenshot_path}")

    # Initialize OCR reader
    reader = easyocr.Reader(['en'], gpu=False)

    # Create region selector
    selector = RegionSelector(screenshot)
    selected_region = selector.run()

    if selected_region is None:
        print("Selection cancelled.")
        return

    left, top, width, height = selected_region
    print(f"Selected region: left={left}, top={top}, width={width}, height={height}")

    # Crop the screenshot to the selected region (using original screenshot)
    cropped_screenshot = screenshot.crop((left, top, left + width, top + height))
    cropped_path = os.path.join(output_dir, f"cropped_{timestamp}.png")
    cropped_screenshot.save(cropped_path)
    print(f"Cropped screenshot saved: {cropped_path}")

    # Run OCR on the cropped image
    img_np = np.array(cropped_screenshot)
    results = reader.readtext(img_np)

    # Extract text and coordinates
    ocr_data = []
    for (bbox, text, confidence) in results:
        # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        x1, y1 = bbox[0]
        x2, y2 = bbox[2]  # bottom-right corner
        ocr_data.append({
            "text": text,
            "confidence": float(confidence),
            "bbox": {
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2)
            }
        })

    # Combine all text
    full_text = " ".join([item["text"] for item in ocr_data])

    # Save OCR results to JSON
    data = {
        "timestamp": timestamp,
        "region": {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        },
        "full_text": full_text,
        "ocr_results": ocr_data,
        "screenshot_path": full_screenshot_path,
        "cropped_path": cropped_path
    }

    json_path = os.path.join(output_dir, f"ocr_data_{timestamp}.json")
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"OCR data saved: {json_path}")
    print(f"Recognized text: {full_text}")

if __name__ == "__main__":
    take_screenshot_and_ocr()
