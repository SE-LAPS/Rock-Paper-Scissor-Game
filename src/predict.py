import cv2
import numpy as np
import tensorflow as tf
import os
import sys

# Local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.preprocess import preprocess_frame

# Load model
model = tf.keras.models.load_model('models/gesture_model.h5')
CATEGORIES = ['rock', 'paper', 'scissors', 'lizard', 'spock']
IMG_SIZE = 224

# Webcam
cap = cv2.VideoCapture(0)
window_name = "Live Gesture Prediction"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

print("[INFO] Press SPACE to capture 30-frame gesture. ESC to exit.")

buffering = False
buffer = []
final_prediction = []

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    original, skin_mask, largest_only = preprocess_frame(frame)
    display_frame = original.copy()

    # Prepare processed view for feedback
    processed_bgr = cv2.cvtColor(largest_only, cv2.COLOR_GRAY2BGR)
    processed_bgr = cv2.resize(processed_bgr, (224, 224))

    key = cv2.waitKey(1)

    # Begin buffering 30 frames after SPACE
    if key == 32 and not buffering:
        print("[INFO] Capturing gesture over 30 frames...")
        buffering = True
        buffer = []
        final_prediction = []

    if buffering:
        resized = cv2.resize(largest_only, (IMG_SIZE, IMG_SIZE))
        normalized = resized / 255.0
        input_img = normalized.reshape(1, IMG_SIZE, IMG_SIZE, 1)
        pred = model.predict(input_img, verbose=0)[0]
        buffer.append(pred)

        if len(buffer) == 30:
            print("[INFO] Processing batch prediction...")
            avg_pred = np.mean(buffer, axis=0)
            final_prediction = list(zip(CATEGORIES, avg_pred))
            final_prediction.sort(key=lambda x: x[1], reverse=True)
            buffering = False

    # Display prediction results if available
    if final_prediction:
        y_offset = 30
        for idx, (label, confidence) in enumerate(final_prediction):
            text = f"{label}: {confidence * 100:.2f}%"
            color = (0, 255, 0) if idx == 0 else (255, 255, 255)
            thickness = 2 if idx == 0 else 1
            font_scale = 0.9 if idx == 0 else 0.7
            cv2.putText(display_frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
            y_offset += 30

    # Combine original + processed preview side by side
    h1, w1, _ = display_frame.shape
    h2, w2, _ = processed_bgr.shape
    if h1 != h2:
        display_frame = cv2.resize(display_frame, (w1, h2))
    combined = np.hstack((display_frame, processed_bgr))

    cv2.imshow(window_name, combined)

    if key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
