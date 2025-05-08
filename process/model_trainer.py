# process/model_trainer.py

import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from PySide6.QtCore import QObject, Signal, Slot, QThread

IMG_SIZE = 224
DATA_DIR = 'data'
CATEGORIES = ['rock', 'paper', 'scissors', 'lizard', 'spock']

class ModelTrainer(QObject):
    training_started = Signal()
    training_finished = Signal(str)

    def __init__(self):
        super().__init__()

    def load_data(self):
        data, labels = [], []
        for category in CATEGORIES:
            path = os.path.join(DATA_DIR, category)
            for img_name in os.listdir(path):
                img_path = os.path.join(path, img_name)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE)) / 255.0
                data.append(img)
                labels.append(category)
        return np.array(data), np.array(labels)

    def build_model(self, num_classes):
        model = Sequential([
            Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 1)),
            MaxPooling2D(2, 2),
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D(2, 2),
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D(2, 2),
            Flatten(),
            Dense(128, activation='relu'),
            Dropout(0.5),
            Dense(num_classes, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    @Slot()
    def train(self):
        self.training_started.emit()
        try:
            X, y = self.load_data()
            X = X.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

            lb = LabelBinarizer()
            y = lb.fit_transform(y)

            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

            model = self.build_model(len(CATEGORIES))
            model.fit(X_train, y_train, epochs=20, validation_data=(X_val, y_val), batch_size=32)

            os.makedirs('models', exist_ok=True)
            model.save('models/gesture_model.h5')
            self.training_finished.emit("Model saved to models/gesture_model.h5")

        except Exception as e:
            self.training_finished.emit(f"Training failed: {str(e)}")
