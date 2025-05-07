# pages/game_page/game_page.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np

from pages.widgets.vs_widget import VSWidget
from process.hand_processing import preprocess_frame, get_hand_contours
from process.camera_manager import CameraManager

class GamePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #3b1d9e; 
                color: white;
            }
            QLabel#title_label {
                font-size: 24pt;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout(self)

        nav_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Home")
        back_button.setFixedWidth(150)
        back_button.clicked.connect(self.go_back_to_home)
        nav_layout.addWidget(back_button)

        training_button = QPushButton("Go to Training Page")
        training_button.setFixedWidth(180)
        training_button.clicked.connect(self.go_to_training)
        nav_layout.addWidget(training_button)

        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        title_label = QLabel("Rock Paper Scissors")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        main_layout.addWidget(title_label)

        game_layout = QHBoxLayout()

        player_layout = QVBoxLayout()
        self.player_camera_feed = QLabel("Initializing Camera...")
        self.player_camera_feed.setFixedSize(250, 250)
        self.player_camera_feed.setStyleSheet("border: 2px solid green;")
        self.player_camera_feed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_layout.addWidget(self.player_camera_feed)
        game_layout.addLayout(player_layout)

        middle_layout = QVBoxLayout()
        self.vs_widget = VSWidget()
        middle_layout.addWidget(self.vs_widget)
        game_layout.addLayout(middle_layout)

        computer_layout = QVBoxLayout()
        self.computer_img = QLabel()
        self.computer_img.setFixedSize(250, 250)
        self.computer_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.computer_img.setStyleSheet("border: 2px solid red;")
        default_pixmap = QPixmap("assets/images/rock.png")
        self.computer_img.setPixmap(default_pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))
        computer_layout.addWidget(self.computer_img)
        game_layout.addLayout(computer_layout)

        main_layout.addLayout(game_layout)
        main_layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        self.start_camera()

    def start_camera(self):
        self.capture = CameraManager.get_instance().acquire_camera()
        if not self.capture.isOpened():
            self.player_camera_feed.setText("Camera Error")
            return
        self.timer.start(60)

    def update_camera_frame(self):
        if not self.capture or not self.capture.isOpened():
            return

        ret, frame = self.capture.read()
        if not ret or frame is None:
            return

        frame = cv2.resize(frame, (320, 240))
        original, _, mask = preprocess_frame(frame)
        contoured = get_hand_contours(mask, original)
        contoured = cv2.resize(contoured, (250, 250))
        contoured_rgb = cv2.cvtColor(contoured, cv2.COLOR_BGR2RGB)

        h, w, ch = contoured_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(contoured_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.player_camera_feed.setPixmap(pixmap)

    def stop_camera(self):
        if self.timer.isActive():
            self.timer.stop()
        CameraManager.get_instance().release_camera()

    def go_back_to_home(self):
        self.stop_camera()
        if self.parent_window and hasattr(self.parent_window, 'stack'):
            home_widget = self.parent_window.home_page
            self.parent_window.stack.setCurrentWidget(home_widget)

    def go_to_training(self):
        self.stop_camera()
        if self.parent_window and hasattr(self.parent_window, 'stack'):
            training_widget = self.parent_window.training_page
            self.parent_window.stack.setCurrentWidget(training_widget)

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()
