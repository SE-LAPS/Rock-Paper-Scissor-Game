# src/predict.py

import cv2
import sys
import os
import numpy as np

# Make sure we can import from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.preprocess import preprocess_frame, get_hand_contours

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Webcam not accessible.")
        return

    print("[INFO] Press ESC to exit...")
    cv2.namedWindow("Hand Gesture Detection [Gray | Threshold | Contours]", cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read from webcam.")
            break

        print("Captured frame")

        original, gray, thresh = preprocess_frame(frame)
        contoured = get_hand_contours(thresh, original)

        stacked = np.hstack((
            cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR),
            cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR),
            contoured
        ))

        cv2.imshow("Hand Gesture Detection [Gray | Threshold | Contours]", stacked)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
