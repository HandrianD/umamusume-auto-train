import cv2
import pytesseract
import os

VIDEO_PATH = 'claw_machine_recording.avi'  # Path to your recorded video
OUTPUT_DIR = 'ocr_frames'  # Directory to save frames and OCR results
FRAME_INTERVAL = 10  # Analyze every Nth frame (adjust as needed)

# Optional: set tesseract cmd path if not in PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def analyze_video(video_path=VIDEO_PATH, output_dir=OUTPUT_DIR, frame_interval=FRAME_INTERVAL):
    ensure_dir(output_dir)
    cap = cv2.VideoCapture(video_path)
    frame_num = 0
    ocr_results = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_num % frame_interval == 0:
            # Optionally crop to region of interest here
            # roi = frame[y1:y2, x1:x2]
            roi = frame
            text = pytesseract.image_to_string(roi)
            ocr_results.append({'frame': frame_num, 'text': text})
            # Save frame and OCR result
            frame_file = os.path.join(output_dir, f'frame_{frame_num}.png')
            with open(os.path.join(output_dir, f'ocr_{frame_num}.txt'), 'w', encoding='utf-8') as f:
                f.write(text)
            cv2.imwrite(frame_file, roi)
            print(f'Frame {frame_num}:\n{text}\n---')
        frame_num += 1
    cap.release()
    print(f'OCR analysis complete. Results saved in {output_dir}')
    return ocr_results

if __name__ == '__main__':
    analyze_video()
