from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QComboBox, QMessageBox, QDialog, QGridLayout
)
from PySide6.QtCore import QTimer, Qt, QEvent
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
        self.recording = False
        self.record_images = []
        self.init_ui()
        self.installEventFilter(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.bulk_timer = QTimer(self)
        self.bulk_timer.timeout.connect(self.capture_bulk_frame)

        self.record_timer = QTimer(self)
        self.record_timer.timeout.connect(self.capture_record_frame)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Top controls
        top_row = QHBoxLayout()
        self.label_combo = QComboBox()
        self.label_combo.addItems(["rock", "paper", "scissors", "spock", "lizard"])
        self.label_combo.currentTextChanged.connect(self.change_label)
        top_row.addWidget(QLabel("Gesture:"))
        top_row.addWidget(self.label_combo)

        self.retrain_button = QPushButton("Retrain Model")
        self.retrain_button.setEnabled(False)
        top_row.addStretch()
        top_row.addWidget(self.retrain_button)
        layout.addLayout(top_row)

        # Camera preview + recording indicator
        self.image_display = QLabel("Camera Initializing...")
        self.image_display.setFixedSize(800, 400)
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setStyleSheet("border: 3px solid green; background-color: black;")
        layout.addWidget(self.image_display)

        self.record_label = QLabel("")
        self.record_label.setAlignment(Qt.AlignCenter)
        self.record_label.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")
        layout.addWidget(self.record_label)

        # Bottom buttons
        button_row = QHBoxLayout()

        self.capture_btn = QPushButton("Hold to Capture")
        self.capture_btn.pressed.connect(self.start_bulk_capture)
        self.capture_btn.released.connect(self.stop_bulk_capture)
        button_row.addWidget(self.capture_btn)

        self.single_btn = QPushButton("Capture One")
        self.single_btn.clicked.connect(self.capture_single_frame)
        button_row.addWidget(self.single_btn)

        button_row.addStretch()

        self.exit_btn = QPushButton("Back to Game")
        self.exit_btn.clicked.connect(self.go_back_to_game)
        button_row.addWidget(self.exit_btn)

        layout.addLayout(button_row)

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

    def start_bulk_capture(self):
        if not hasattr(self, 'current_thresh'):
            return
        self.bulk_images = []
        self.bulk_timer.start(100)

    def stop_bulk_capture(self):
        self.bulk_timer.stop()
        count = len(self.bulk_images)
        if count == 0:
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("Bulk Capture Complete")
        msg.setText(f"{count} images captured for '{self.current_label}'.")
        msg.setInformativeText("Would you like to save them?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)

        result = msg.exec()

        if result == QMessageBox.Yes:
            label_dir = os.path.join(self.base_dir, self.current_label)
            os.makedirs(label_dir, exist_ok=True)
            for img in self.bulk_images:
                filename = f"{self.current_label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
                path = os.path.join(label_dir, filename)
                cv2.imwrite(path, img)
            QMessageBox.information(self, "Saved", f"{count} images saved to {label_dir}")
        else:
            QMessageBox.information(self, "Discarded", "Captured images discarded.")

    def capture_bulk_frame(self):
        if len(self.bulk_images) < 100 and hasattr(self, 'current_thresh'):
            self.bulk_images.append(self.current_thresh.copy())

    def capture_single_frame(self):
        if hasattr(self, 'current_thresh'):
            label_dir = os.path.join(self.base_dir, self.current_label)
            os.makedirs(label_dir, exist_ok=True)
            filename = f"{self.current_label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            path = os.path.join(label_dir, filename)
            cv2.imwrite(path, self.current_thresh)
            QMessageBox.information(self, "Captured", f"Saved to: {path}")

    def change_label(self, label):
        self.current_label = label

    def go_back_to_game(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.bulk_timer.isActive():
            self.bulk_timer.stop()
        if self.record_timer.isActive():
            self.record_timer.stop()

        CameraManager.get_instance().release_camera()
        QApplication.processEvents()

        if self.parent_window and hasattr(self.parent_window, 'stack'):
            self.parent_window.stack.setCurrentWidget(self.parent_window.game_page)

    # ───────────────────────────────────────────────
    # SPACEBAR: TOGGLE RECORDING MODE
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
        print("Started recording...")

    def stop_recording(self):
        self.recording = False
        self.record_timer.stop()
        self.record_label.setText("")
        print("Stopped recording.")
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
        for i, img in enumerate(self.record_images[:30]):  # max 30 for UI
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            h, w = img.shape
            qt_img = QImage(img_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_img).scaled(100, 100, Qt.KeepAspectRatio)
            label = QLabel()
            label.setPixmap(pixmap)
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
                path = os.path.join(label_dir, filename)
                cv2.imwrite(path, img)
            dialog.accept()

        def discard():
            dialog.reject()

        save_btn.clicked.connect(save)
        discard_btn.clicked.connect(discard)

        dialog.exec()
