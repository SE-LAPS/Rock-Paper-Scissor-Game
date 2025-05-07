# main.py

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QPropertyAnimation, QRect, QByteArray

from pages.home_page.home_page import HomePage
from pages.game_page.game_page import GamePage
from pages.training_page.training_page import TrainingPage

import sys

class MainWindow(QMainWindow):
    """Main window that manages stacked pages and transitions."""

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("assets/icons/icon.png"))
        self.setWindowTitle("Rock, Paper, Scissors")
        self.setStyleSheet("background-color: #3b1d9e; color: white;")
        self.resize(1400, 800)

        self.stack = QStackedWidget()
        self.home_page = HomePage(self.transition_to_game)
        self.training_page = TrainingPage(parent=self)

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.training_page)

        self.setCentralWidget(self.stack)

    def transition_to_game(self):
        """Animate transition from home to game page."""
        if not hasattr(self, 'game_page'):
            self.game_page = GamePage(self)
            self.stack.addWidget(self.game_page)
        self.stack.setCurrentWidget(self.game_page)

    def animate_transition(self):
        """Smooth animation for the stacked widget switch."""
        current_widget = self.stack.currentWidget()
        current_widget.setGeometry(QRect(800, 0, 800, 500))

        animation = QPropertyAnimation(current_widget, QByteArray(b"geometry"))
        animation.setDuration(500)
        animation.setStartValue(QRect(800, 0, 800, 500))
        animation.setEndValue(QRect(0, 0, 800, 500))
        animation.start()
        # Store animation to prevent garbage collection
        self.animation = animation


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
