import os
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from process.hand_processing import preprocess_frame


class GestureRecognizer:
    def __init__(self, model_path="models/gesture_model.h5"):
        self.model = self._load_model(model_path)
        self.labels = ["rock", "paper", "scissors", "lizard", "spock"]
        self.img_size = 224

    def _load_model(self, path):
        if not os.path.exists(path):
            print(f"[WARNING] Gesture model not found at '{path}'. Predictions will be random.")
            return None
        try:
            model = load_model(path)
            print(f"[INFO] Gesture model loaded from {path}")
            return model
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            return None

    def process_frame(self, frame):
        """
        Accepts a BGR frame, returns (predicted_label, processed_frame_for_display)
        """
        if self.model is None:
            return None, frame

        # Preprocess frame to get thresholded hand
        _, _, thresh = preprocess_frame(frame)
        try:
            # Resize for model input
            resized = cv2.resize(thresh, (self.img_size, self.img_size))
            normalized = resized.astype(np.float32) / 255.0
            input_tensor = np.expand_dims(normalized, axis=(0, -1))  # shape: (1, 224, 224, 1)

            # Predict
            prediction = self.model.predict(input_tensor, verbose=0)[0]
            label_index = np.argmax(prediction)
            label = self.labels[label_index]

            return label, cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            return None, frame
