# Refactored TrainingPage with button-based bulk capture and scrollable preview
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QComboBox, QMessageBox, QDialog, QGridLayout,
    QScrollArea, QFrame
)
from PySide6.QtCore import QTimer, Qt, QThread
from PySide6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import os
from datetime import datetime

from process.hand_processing import preprocess_frame
from process.camera_manager import CameraManager


class TrainingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.capture = None
        self.current_label = "rock"
        self.base_dir = "data"
        self.bulk_images = []

        self.init_ui()
        self.setup_training_thread()

        self.timer = QTimer(self, timeout=self.update_frame)
        self.bulk_timer = QTimer(self, timeout=self.capture_bulk_frame)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 20, 30, 20)
        self.layout.setSpacing(15)

        self.init_controls()
        self.init_camera_feed()
        self.init_buttons()
        self.init_status_labels()

    def init_controls(self):
        top_row = QHBoxLayout()
        self.label_combo = QComboBox()
        self.label_combo.addItems(["rock", "paper", "scissors", "spock", "lizard"])
        self.label_combo.currentTextChanged.connect(self.change_label)
        top_row.addWidget(QLabel("Gesture:"))
        top_row.addWidget(self.label_combo)

        self.retrain_button = QPushButton("Retrain Model", enabled=True)
        top_row.addStretch()
        top_row.addWidget(self.retrain_button)

        self.layout.addLayout(top_row)

    def init_camera_feed(self):
        self.image_display = QLabel("Initializing Camera...")
        self.image_display.setFixedSize(800, 400)
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setStyleSheet("border: 2px solid #4CAF50; background-color: #000;")
        self.layout.addWidget(self.image_display)

    def init_buttons(self):
        buttons = QHBoxLayout()

        self.capture_btn = QPushButton("Hold to Capture")
        self.capture_btn.pressed.connect(self.start_bulk_capture)
        self.capture_btn.released.connect(self.stop_bulk_capture)
        buttons.addWidget(self.capture_btn)

        self.single_btn = QPushButton("Capture One")
        self.single_btn.clicked.connect(self.capture_single_frame)
        buttons.addWidget(self.single_btn)

        buttons.addStretch()

        self.exit_btn = QPushButton("Back to Game")
        self.exit_btn.clicked.connect(self.go_back_to_game)
        buttons.addWidget(self.exit_btn)

        self.layout.addLayout(buttons)

        self.counter_label = QLabel("Images Captured: 0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.counter_label)

    def init_status_labels(self):
        self.train_label = QLabel("", alignment=Qt.AlignCenter)
        self.train_label.setStyleSheet("color: orange; font-weight: bold; font-size: 16px;")
        self.layout.addWidget(self.train_label)

    def showEvent(self, event):
        super().showEvent(event)
        self.setup_camera()
        self.setFocus()

    def setup_camera(self):
        if self.capture and self.capture.isOpened():
            return
        self.capture = CameraManager.get_instance().acquire_camera()
        if not self.timer.isActive():
            self.timer.start(30)

    def update_frame(self):
        if not self.capture or not self.capture.isOpened():
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        original, _, thresh = preprocess_frame(frame)
        original_resized = cv2.resize(original, (400, 400))
        thresh_resized = cv2.resize(thresh, (400, 400))
        processed_bgr = cv2.cvtColor(thresh_resized, cv2.COLOR_GRAY2BGR)

        preview = np.hstack((original_resized, processed_bgr))
        preview = cv2.resize(preview, (800, 400))
        preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)

        h, w, ch = preview.shape
        qt_img = QImage(preview.data, w, h, ch * w, QImage.Format_RGB888)
        self.image_display.setPixmap(QPixmap.fromImage(qt_img))

        self.current_thresh = thresh_resized

    def capture_single_frame(self):
        if hasattr(self, 'current_thresh'):
            label_dir = os.path.join(self.base_dir, self.current_label)
            os.makedirs(label_dir, exist_ok=True)
            filename = f"{self.current_label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            filepath = os.path.join(label_dir, filename)
            cv2.imwrite(filepath, self.current_thresh)
            QMessageBox.information(self, "Image Captured", f"Saved: {filepath}")

    def start_bulk_capture(self):
        self.bulk_images.clear()
        self.counter_label.setText("Images Captured: 0")
        self.bulk_timer.start(100)

    def stop_bulk_capture(self):
        self.bulk_timer.stop()
        if not self.bulk_images:
            return
        self.show_bulk_preview()

    def capture_bulk_frame(self):
        if hasattr(self, 'current_thresh') and len(self.bulk_images) < 100:
            self.bulk_images.append(self.current_thresh.copy())
            self.counter_label.setText(f"Images Captured: {len(self.bulk_images)}")

    def show_bulk_preview(self):
        dialog = QDialog(self, windowTitle="Save Captured Images?")
        layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        container = QFrame()
        grid = QGridLayout(container)

        for i, img in enumerate(self.bulk_images):
            qt_img = QImage(cv2.cvtColor(img, cv2.COLOR_GRAY2RGB).data, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
            label = QLabel()
            label.setPixmap(QPixmap.fromImage(qt_img).scaled(100, 100, Qt.KeepAspectRatio))
            grid.addWidget(label, i // 10, i % 10)

        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        discard_btn = QPushButton("Discard")
        buttons.addWidget(save_btn)
        buttons.addWidget(discard_btn)
        layout.addLayout(buttons)

        save_btn.clicked.connect(lambda: self.save_bulk_images(dialog))
        discard_btn.clicked.connect(dialog.reject)

        dialog.exec()

    def save_bulk_images(self, dialog):
        label_dir = os.path.join(self.base_dir, self.current_label)
        os.makedirs(label_dir, exist_ok=True)
        for img in self.bulk_images:
            filename = f"{self.current_label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            cv2.imwrite(os.path.join(label_dir, filename), img)
        dialog.accept()

    def change_label(self, label):
        self.current_label = label

    def go_back_to_game(self):
        for t in (self.timer, self.bulk_timer):
            t.stop()
        CameraManager.get_instance().release_camera()
        self.parent_window.stack.setCurrentWidget(self.parent_window.game_page)

    def setup_training_thread(self):
        from process.model_trainer import ModelTrainer
        self.training_thread = QThread()
        self.trainer = ModelTrainer()
        self.trainer.moveToThread(self.training_thread)

        self.trainer.training_started.connect(lambda: self.train_label.setText("⏳ Training in progress..."))
        self.trainer.training_finished.connect(self.on_training_done)
        self.training_thread.started.connect(self.trainer.train)

        self.retrain_button.clicked.connect(self.start_training)

    def start_training(self):
        if not self.training_thread.isRunning():
            self.training_thread.start()

    def on_training_done(self, message):
        self.train_label.setText(message)
        self.training_thread.quit()
