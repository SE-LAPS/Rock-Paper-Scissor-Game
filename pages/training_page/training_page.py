# pages/training_page/training_page.py

import os
from datetime import datetime
import cv2
import numpy as np
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap

from process.hand_processing import preprocess_frame
from process.camera_manager import CameraManager


class TrainingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.capture = None
        self.current_label = "rock"
        self.base_dir = "data"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.label_combo = QComboBox()
        self.label_combo.addItems(["rock", "paper", "scissors", "spock", "lizard"])
        self.label_combo.currentTextChanged.connect(self.change_label)
        layout.addWidget(self.label_combo)

        self.image_display = QLabel("Camera Initializing...")
        self.image_display.setFixedSize(500, 250)
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setStyleSheet("border: 2px solid green;")
        layout.addWidget(self.image_display)

        btn_layout = QHBoxLayout()

        self.capture_btn = QPushButton("Capture")
        self.capture_btn.clicked.connect(self.capture_frame)
        btn_layout.addWidget(self.capture_btn)

        self.exit_btn = QPushButton("Back to Game")
        self.exit_btn.clicked.connect(self.go_back_to_game)
        btn_layout.addWidget(self.exit_btn)

        layout.addLayout(btn_layout)

    def showEvent(self, event):
        super().showEvent(event)
        self.setup_camera()

    def setup_camera(self):
        # Prevent re-acquiring if already active
        if self.capture and self.capture.isOpened():
            return

        self.capture = CameraManager.get_instance().acquire_camera()
        if not self.timer.isActive():
            self.timer.start(30)

    def change_label(self, label):
        self.current_label = label

    def update_frame(self):
        if not self.capture or not self.capture.isOpened():
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        original, _, thresh = preprocess_frame(frame)
        original_resized = cv2.resize(original, (250, 250))
        thresh_resized = cv2.resize(thresh, (250, 250))
        processed_bgr = cv2.cvtColor(thresh_resized, cv2.COLOR_GRAY2BGR)

        preview = np.hstack((original_resized, processed_bgr))
        preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        h, w, ch = preview.shape
        bytes_per_line = ch * w
        qt_img = QImage(preview.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.image_display.setPixmap(QPixmap.fromImage(qt_img))

        self.current_thresh = thresh_resized

    def capture_frame(self):
        label_dir = os.path.join(self.base_dir, self.current_label)
        os.makedirs(label_dir, exist_ok=True)
        filename = f"{self.current_label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        path = os.path.join(label_dir, filename)
        cv2.imwrite(path, self.current_thresh)
        QMessageBox.information(self, "Captured", f"Saved to: {path}")

    def go_back_to_game(self):
        if self.timer.isActive():
            self.timer.stop()
        CameraManager.get_instance().release_camera()
        QApplication.processEvents()

        if self.parent_window and hasattr(self.parent_window, 'stack'):
            self.parent_window.stack.setCurrentWidget(self.parent_window.game_page)
