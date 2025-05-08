from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QImage
import cv2
import numpy as np
import random

from pages.widgets.vs_widget import VSWidget
from process.gesture_recognizer import GestureRecognizer


class GamePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.gesture_recognizer = GestureRecognizer()
        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)
        self.init_ui()
        self.start_camera()

    def init_ui(self):
        self.setStyleSheet("background-color: #3b1d9e; color: white;")
        main_layout = QVBoxLayout(self)

        nav_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Home")
        back_button.clicked.connect(self.go_back_to_home)
        nav_layout.addWidget(back_button)
        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        title = QLabel("Rock Paper Scissors")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        game_layout = QHBoxLayout()

        # Player camera
        self.live_feed_label = QLabel("Initializing...")
        self.live_feed_label.setFixedSize(250, 250)
        self.live_feed_label.setAlignment(Qt.AlignCenter)
        self.live_feed_label.setStyleSheet("border: 2px solid green;")
        game_layout.addWidget(self.live_feed_label)

        self.vs_widget = VSWidget()
        game_layout.addWidget(self.vs_widget)

        # Computer image
        self.computer_img = QLabel()
        self.computer_img.setFixedSize(250, 250)
        self.computer_img.setAlignment(Qt.AlignCenter)
        self.computer_img.setStyleSheet("border: 2px solid red;")
        game_layout.addWidget(self.computer_img)

        main_layout.addLayout(game_layout)

        # Game info
        self.status_label = QLabel("Press Start to begin!")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 16))
        main_layout.addWidget(self.status_label)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_game)
        main_layout.addWidget(self.start_button)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(self.result_label)

        # Game logic state
        self.player_gesture = None
        self.timer_countdown = QTimer()
        self.timer_countdown.setInterval(1000)
        self.timer_countdown.timeout.connect(self.update_countdown)
        self.time_left = 3

    def start_camera(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            self.live_feed_label.setText("Camera Error")
            return
        self.timer.start(30)

    def update_camera_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        gesture, processed_frame = self.gesture_recognizer.process_frame(frame)

        if self.timer_countdown.isActive():
            self.player_gesture = gesture

        rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        qt_img = QImage(rgb.data, rgb.shape[1], rgb.shape[0], rgb.strides[0], QImage.Format_RGB888)
        self.live_feed_label.setPixmap(QPixmap.fromImage(qt_img).scaled(250, 250, Qt.KeepAspectRatio))

    def start_game(self):
        self.result_label.setText("")
        self.player_gesture = None
        self.time_left = 3
        self.status_label.setText(f"Show gesture in: {self.time_left}")
        self.timer_countdown.start()

    def update_countdown(self):
        self.time_left -= 1
        if self.time_left > 0:
            self.status_label.setText(f"Show gesture in: {self.time_left}")
        else:
            self.timer_countdown.stop()
            self.status_label.setText("Now!")
            self.evaluate_result()

    def evaluate_result(self):
        comp_gesture = random.choice(self.gesture_recognizer.labels)
        comp_pixmap = QPixmap(f"assets/images/{comp_gesture}.png")
        self.computer_img.setPixmap(comp_pixmap.scaled(250, 250, Qt.KeepAspectRatio))

        result = self.determine_winner(self.player_gesture, comp_gesture)
        self.result_label.setText(f"You: {self.player_gesture or 'None'} | Pi: {comp_gesture} → {result}")

    def determine_winner(self, player, computer):
        win_map = {
            "rock": ["scissors", "lizard"],
            "paper": ["rock", "spock"],
            "scissors": ["paper", "lizard"],
            "lizard": ["spock", "paper"],
            "spock": ["scissors", "rock"]
        }
        if not player:
            return "No gesture"
        if player == computer:
            return "Tie"
        elif computer in win_map[player]:
            return "You Win"
        else:
            return "Pi Wins"

    def go_back_to_home(self):
        self.timer.stop()
        if self.capture and self.capture.isOpened():
            self.capture.release()
        if self.parent_window:
            self.parent_window.stack.setCurrentWidget(self.parent_window.home_page)

    def closeEvent(self, event):
        self.timer.stop()
        if self.capture and self.capture.isOpened():
            self.capture.release()
        event.accept()
