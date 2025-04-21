# src/capture.py

import cv2
import os
import sys
from datetime import datetime
import numpy as np

# Local import for preprocessing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.preprocess import preprocess_frame

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    if len(sys.argv) != 2:
        print("Usage: python capture.py <gesture>")
        return

    gesture = sys.argv[1].lower()
    save_dir = os.path.join("data", gesture)
    ensure_dir(save_dir)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Webcam not accessible.")
        return

    print(f"[INFO] Starting capture for gesture: {gesture}")
    print("[INFO] Press SPACE to capture, ESC to exit.")
    count = len(os.listdir(save_dir))

    window_name = f"Capture Gesture: {gesture}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from webcam.")
            break

        original, skin_mask, thresh = preprocess_frame(frame)

        # Upscale original frame (2x)
        original_upscaled = cv2.resize(original, (0, 0), fx=2, fy=2)

        # Keep processed image as is, convert to BGR for display
        processed_bgr = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        # Make heights match by padding the processed image
        h1, w1, _ = original_upscaled.shape
        h2, w2, _ = processed_bgr.shape

        if h1 > h2:
            pad = np.zeros((h1 - h2, w2, 3), dtype=np.uint8)
            processed_padded = np.vstack((processed_bgr, pad))
        else:
            processed_padded = processed_bgr

        # Combine side-by-side
        combined_view = np.hstack((original_upscaled, processed_padded))

        # Show the combined view
        cv2.imshow(window_name, combined_view)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            filename = f"{gesture}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            filepath = os.path.join(save_dir, filename)
            cv2.imwrite(filepath, thresh)
            count += 1
            print(f"[+] Saved: {filepath}")


    cap.release()
    cv2.destroyAllWindows()
    print(f"[INFO] Has {count} samples for '{gesture}' total.")

if __name__ == "__main__":
    main()
