import cv2
import numpy as np
import tensorflow as tf

class GestureClassifier:
    def __init__(self, model_path='models/gesture_model.h5', categories=None, img_size=224):
        self.model = tf.keras.models.load_model(model_path)
        self.categories = categories or ['rock', 'paper', 'scissors', 'lizard', 'spock']
        self.img_size = img_size

    def preprocess(self, img):
        resized = cv2.resize(img, (self.img_size, self.img_size))
        normalized = resized / 255.0
        return normalized.reshape(1, self.img_size, self.img_size, 1)

    def predict_top_k(self, img, k=5):
        processed = self.preprocess(img)
        preds = self.model.predict(processed, verbose=0)[0]
        results = list(zip(self.categories, preds))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def predict_with_buffer(self, frames):
        buffer_preds = []
        for img in frames:
            processed = self.preprocess(img)
            pred = self.model.predict(processed, verbose=0)[0]
            buffer_preds.append(pred)

        avg_pred = np.mean(buffer_preds, axis=0)
        results = list(zip(self.categories, avg_pred))
        results.sort(key=lambda x: x[1], reverse=True)
        return results, avg_pred  # full average vector returned optionally
