from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpacerItem, 
    QSizePolicy, QFrame
)

class HomePage(QWidget):
    """Landing page with a single combined image and navigation buttons."""

    def __init__(self, navigate_callback:object):
        super().__init__()
        self.navigate_callback = navigate_callback
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #3b1d9e; 
                color: white;
            }
            QLabel#title_label {
                font-size: 32px;
                font-weight: bold;
            }
            QLabel#description {
                font-size: 16px;
                padding: 15px;
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
            }
            QFrame#container {
                background-color: transparent;
            }
        """)

        # Add a vertical spacer at the top
        top_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        # Create a container for the text content
        text_container = QFrame()
        text_container.setObjectName("container")
        text_container.setMinimumWidth(500)
        text_container.setMaximumWidth(600)
        text_container_layout = QVBoxLayout(text_container)
        text_container_layout.setContentsMargins(10, 10, 10, 10)

        # Title with object name for styling
        title = QLabel("Rock, Paper\nScissors\nLizard, Spock")
        title.setObjectName("title_label")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Description - directly in the layout
        description = QLabel()
        description.setObjectName("description")
        description.setText(
            "Challenge the computer in the expanded version of Rock, Paper, Scissors!\n\n"
            "Make your move - Rock, Paper, Scissors, Lizard, or Spock - and see if you can outsmart the AI.\n\n"
            "As Sheldon Cooper says:\n"
            "'Scissors cuts paper,\n"
            " paper covers rock,\n"
            " rock crushes lizard,\n"
            " lizard poisons Spock,\n"
            " Spock smashes scissors,\n"
            " scissors decapitates lizard,\n"
            " lizard eats paper,\n"
            " paper disproves Spock,\n"
            " Spock vaporizes rock,\n"
            " and rock crushes scissors!'"
        )
        description.setWordWrap(True)
        description.setMinimumHeight(300)
        
        # Buttons
        start_btn = QPushButton("Start Game")
        start_btn.setStyleSheet(self.button_style())
        start_btn.setMinimumWidth(200)
        start_btn.setMaximumWidth(250)
        start_btn.setMinimumHeight(50)
        start_btn.clicked.connect(self.navigate_callback)

        # Add elements to container
        text_container_layout.addWidget(title)
        text_container_layout.addSpacing(20)
        text_container_layout.addWidget(description)
        text_container_layout.addSpacing(30)
        text_container_layout.addWidget(start_btn, 0, Qt.AlignmentFlag.AlignLeft)
        text_container_layout.addStretch(1)

        # Image on the right
        image_label = QLabel()
        pixmap = QPixmap("assets/images/home_image.png").scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.addSpacing(30)
        main_layout.addWidget(text_container, 4)
        main_layout.addSpacing(30)
        main_layout.addWidget(image_label, 6)
        main_layout.setContentsMargins(20, 20, 20, 20)

    def button_style(self):
        return (
            "QPushButton {"
            "background-color: orange;"
            "color: white;"
            "padding: 15px 30px;"
            "border-radius: 10px;"
            "font-weight: bold;"
            "font-size: 18px;"
            "}"
            "QPushButton:hover {"
            "background-color: #ffb700;"
            "}"
        )
                                  
