import cv2
import numpy as np
import mss
import time

# Settings
MONITOR = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}  # 1080p full screen
OUTPUT_FILE = 'claw_machine_recording.avi'
FPS = 20.0
RECORD_SECONDS = 60  # Change as needed


def record_screen(duration=RECORD_SECONDS, output_file=OUTPUT_FILE, fps=FPS, monitor=MONITOR):
    print(f"Recording {duration} seconds of screen to {output_file}...")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, fps, (monitor['width'], monitor['height']))
    sct = mss.mss()
    start_time = time.time()
    frame_count = 0
    try:
        while True:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            out.write(frame)
            frame_count += 1
            if (time.time() - start_time) > duration:
                break
            # Sleep to match FPS
            time.sleep(max(0, 1.0/fps - 0.001))
    finally:
        out.release()
        print(f"Done! {frame_count} frames saved to {output_file}")

if __name__ == '__main__':
    record_screen()
