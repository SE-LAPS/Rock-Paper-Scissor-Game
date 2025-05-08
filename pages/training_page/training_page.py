# pages/training_page/training_page.py

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QComboBox, QMessageBox, QDialog, QGridLayout
)
from PySide6.QtCore import QTimer, Qt, QEvent, QThread
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
        self.record_images = []
        self.recording = False

        self.init_ui()
        self.setup_training_thread()

        self.installEventFilter(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.bulk_timer = QTimer(self)
        self.bulk_timer.timeout.connect(self.capture_bulk_frame)

        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self.capture_record_frame)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 20, 30, 20)
        self.layout.setSpacing(20)

        # Top controls
        top_row = QHBoxLayout()
        self.label_combo = QComboBox()
        self.label_combo.addItems(["rock", "paper", "scissors", "spock", "lizard"])
        self.label_combo.currentTextChanged.connect(self.change_label)
        top_row.addWidget(QLabel("Gesture:"))
        top_row.addWidget(self.label_combo)

        self.retrain_button = QPushButton("Retrain Model")
        self.retrain_button.setEnabled(True)
        top_row.addStretch()
        top_row.addWidget(self.retrain_button)
        self.layout.addLayout(top_row)

        # Camera feed
        self.image_display = QLabel("Camera Initializing...")
        self.image_display.setFixedSize(800, 400)
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setStyleSheet("border: 3px solid green; background-color: black;")
        self.layout.addWidget(self.image_display)

        # Recording indicator
        self.record_label = QLabel("")
        self.record_label.setAlignment(Qt.AlignCenter)
        self.record_label.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")
        self.layout.addWidget(self.record_label)

        # Buttons row
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

        # Training status label
        self.train_label = QLabel("")
        self.train_label.setAlignment(Qt.AlignCenter)
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
        qt_img = QImage(preview.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.image_display.setPixmap(QPixmap.fromImage(qt_img))

        self.current_thresh = thresh_resized

    def capture_single_frame(self):
        if hasattr(self, 'current_thresh'):
            label_dir = os.path.join(self.base_dir, self.current_label)
            os.makedirs(label_dir, exist_ok=True)
            filename = f"{self.current_label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            cv2.imwrite(os.path.join(label_dir, filename), self.current_thresh)
            QMessageBox.information(self, "Captured", f"Saved to: {filename}")

    def start_bulk_capture(self):
        self.bulk_images = []
        self.bulk_timer.start(100)

    def stop_bulk_capture(self):
        self.bulk_timer.stop()
        if not self.bulk_images:
            return

        response = QMessageBox.question(
            self, "Bulk Capture Complete",
            f"{len(self.bulk_images)} images captured for '{self.current_label}'. Save them?",
            QMessageBox.Yes | QMessageBox.No
        )

        if response == QMessageBox.Yes:
            label_dir = os.path.join(self.base_dir, self.current_label)
            os.makedirs(label_dir, exist_ok=True)
            for img in self.bulk_images:
                filename = f"{self.current_label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
                cv2.imwrite(os.path.join(label_dir, filename), img)
            QMessageBox.information(self, "Saved", f"Images saved to {label_dir}")
        else:
            QMessageBox.information(self, "Discarded", "Images were not saved.")

    def capture_bulk_frame(self):
        if len(self.bulk_images) < 100 and hasattr(self, 'current_thresh'):
            self.bulk_images.append(self.current_thresh.copy())

    def change_label(self, label):
        self.current_label = label

    def go_back_to_game(self):
        self.timer.stop()
        self.bulk_timer.stop()
        self.record_timer.stop()
        CameraManager.get_instance().release_camera()
        QApplication.processEvents()
        self.parent_window.stack.setCurrentWidget(self.parent_window.game_page)

    # ───────────────────────────────────────────────
    # SPACEBAR: TOGGLE RECORDING
    # ───────────────────────────────────────────────
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Space:
            if not self.recording:
                self.start_recording()
            else:
                self.stop_recording()
            return True
        return super().eventFilter(obj, event)

    def start_recording(self):
        self.recording = True
        self.record_images = []
        self.record_timer.start(100)
        self.record_label.setText("● Recording...")

    def stop_recording(self):
        self.recording = False
        self.record_timer.stop()
        self.record_label.setText("")
        self._show_recording_preview()

    def capture_record_frame(self):
        if hasattr(self, 'current_thresh'):
            self.record_images.append(self.current_thresh.copy())

    def _show_recording_preview(self):
        if not self.record_images:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Save Recording?")
        layout = QVBoxLayout(dialog)

        grid = QGridLayout()
        for i, img in enumerate(self.record_images[:30]):
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            qt_img = QImage(img_rgb.data, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)
            label = QLabel()
            label.setPixmap(QPixmap.fromImage(qt_img).scaled(100, 100, Qt.KeepAspectRatio))
            grid.addWidget(label, i // 10, i % 10)

        layout.addLayout(grid)

        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        discard_btn = QPushButton("Discard")
        buttons.addWidget(save_btn)
        buttons.addWidget(discard_btn)
        layout.addLayout(buttons)

        def save():
            label_dir = os.path.join(self.base_dir, self.current_label)
            os.makedirs(label_dir, exist_ok=True)
            for img in self.record_images:
                filename = f"{self.current_label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
                cv2.imwrite(os.path.join(label_dir, filename), img)
            dialog.accept()

        def discard():
            dialog.reject()

        save_btn.clicked.connect(save)
        discard_btn.clicked.connect(discard)

        dialog.exec()

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
