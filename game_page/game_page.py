from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QGraphicsOpacityEffect, 
    QGridLayout, QSizePolicy, QSpacerItem, QMenuBar, QMenu, QDialog,
    QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, QByteArray, QSize
from PySide6.QtGui import QFont, QPixmap, QImage, QColor
import random
import cv2
import numpy as np
from pages.widgets.vs_widget import VSWidget
from pages.game_page.gesture_recognition import GestureRecognizer

class CameraWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Camera Feed")
        self.setFixedSize(640, 480)
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        self.capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        
    def start_camera(self):
        """Attempt to start the camera and return success status"""
        try:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                raise RuntimeError("Could not open camera")
            self.timer.start(30)
            return True
        except Exception as e:
            print(f"Camera error: {str(e)}")
            return False

    def update_frame(self):
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()

    def stop_camera(self):
        if self.capture and self.capture.isOpened():
            self.capture.release()
        self.timer.stop()

    def show_camera(self):
        """Show the camera window and display status message"""
        if self.capture and self.capture.isOpened():
            self.show()
            QMessageBox.information(self, "Camera Status", 
                                   "Camera is now active and showing live feed!")
        else:
            QMessageBox.critical(self, "Camera Error", 
                               "Camera is not available. Please check your camera connection.")

class GamePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gesture_recognizer = GestureRecognizer()
        self.camera_window = None
        self.camera_active = False
        self.player_gesture_pixmap = None
        self.parent_window = parent
        self.init_ui()
        self.initialize_camera()

    def initialize_camera(self):
        """Initialize camera and show appropriate message"""
        self.camera_active = True
        try:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                QMessageBox.warning(self, "Camera Warning", 
                                  "Could not initialize camera. The game will use random gestures instead.\n"
                                  "You can try reconnecting your camera and restarting the game.")
                self.camera_active = False
                self.live_feed_label.setText("No Camera\nRandom Mode")
                self.live_feed_label.setStyleSheet("border: 2px solid yellow; color: yellow; font-size: 16px;")
            else:
                # Start the camera feed timer
                self.camera_timer = QTimer(self)
                self.camera_timer.timeout.connect(self.process_camera_frame)
                self.camera_timer.start(30)  # 30ms = ~33 fps
        except Exception as e:
            QMessageBox.warning(self, "Camera Warning", 
                               f"Camera initialization error: {str(e)}\nThe game will use random gestures instead.")
            self.camera_active = False
            self.live_feed_label.setText("No Camera\nRandom Mode")
            self.live_feed_label.setStyleSheet("border: 2px solid yellow; color: yellow; font-size: 16px;")

    def process_camera_frame(self):
        """Process camera frame and detect gestures"""
        if not self.camera_active or not hasattr(self, 'capture'):
            return

        try:
            if not self.capture.isOpened():
                self.reinitialize_camera()
                return

            ret, frame = self.capture.read()
            if not ret or frame is None or frame.size == 0:
                self.reinitialize_camera()
                return

            # Flip the frame horizontally for a more natural view
            frame = cv2.flip(frame, 1)
            
            # Process frame with gesture recognizer
            gesture, processed_frame = self.gesture_recognizer.process_frame(frame)
            
            # Convert frame to QPixmap for display
            try:
                processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = processed_frame.shape
                bytes_per_line = ch * w
                image = QImage(processed_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(image)
                
                # Display in the player's gesture area
                self.live_feed_label.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))
                
                # If a gesture is detected during countdown, store it
                if self.timer.isActive() and gesture:
                    self.player_gesture_pixmap = pixmap.copy()
                    self.player_gesture = gesture
            except Exception as e:
                print(f"Error processing camera frame: {str(e)}")
        except Exception as e:
            print(f"Camera error: {str(e)}")
            # Try to recover
            self.reinitialize_camera()

    def reinitialize_camera(self):
        """Try to recover the camera connection"""
        try:
            # Clean up existing resources
            if hasattr(self, 'capture') and self.capture:
                self.capture.release()
                
            # Try to reopen
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                self.camera_active = False
                self.live_feed_label.setText("Camera Error\nRestart Game")
                self.live_feed_label.setStyleSheet("border: 2px solid red; color: red; font-size: 16px;")
            else:
                self.camera_active = True
        except Exception as e:
            print(f"Failed to reinitialize camera: {str(e)}")
            self.camera_active = False

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
            QLabel#result_label {
                font-size: 18pt;
                color: lightgreen;
            }
            QLabel#scoreboard {
                font-size: 16pt;
                color: white;
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        self.choices = ["rock", "paper", "scissors"]
        self.image_paths = {
            "rock": "assets/images/rock.png",
            "paper": "assets/images/paper.png",
            "scissors": "assets/images/scissors.png"
        }

        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Top navigation bar
        nav_bar = QWidget()
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(10, 5, 10, 5)
        
        # Back button
        back_button = QPushButton("← Back to Home")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 153, 0, 0.8);
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 153, 0, 1.0);
            }
        """)
        back_button.setFixedWidth(150)
        back_button.clicked.connect(self.go_back_to_home)
        
        # Add to nav bar
        nav_layout.addWidget(back_button)
        nav_layout.addStretch()
        
        # Create the "Actions" menu button
        actions_button = QPushButton("Actions ▾")
        actions_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 14px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                color: #ff9900;
            }
        """)
        actions_button.clicked.connect(self.show_actions_menu)
        nav_layout.addWidget(actions_button)
        
        # Add nav bar to main layout
        main_layout.addWidget(nav_bar)
        
        # Title
        title_label = QLabel("Rock Paper Scissors")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        main_layout.addWidget(title_label)
        
        # Scoreboard at the top
        self.scoreboard = QLabel("You: 0  |  Pi: 0")
        self.scoreboard.setObjectName("scoreboard")
        self.scoreboard.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scoreboard.setMaximumHeight(50)
        main_layout.addWidget(self.scoreboard)
        
        # Game area layout
        game_layout = QHBoxLayout()
        
        # Left side - Player
        player_layout = QVBoxLayout()
        self.player_score_label = QLabel("Your Move: ?")
        self.player_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        # Live camera feed for player
        self.live_feed_label = QLabel()
        self.live_feed_label.setFixedSize(250, 250)
        self.live_feed_label.setStyleSheet("border: 2px solid green;")
        self.live_feed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        player_layout.addWidget(self.player_score_label)
        player_layout.addWidget(self.live_feed_label)
        player_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Middle - VS widget
        middle_layout = QVBoxLayout()
        self.vs_widget = VSWidget()
        middle_layout.addWidget(self.vs_widget)
        middle_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Right side - Computer
        computer_layout = QVBoxLayout()
        self.computer_score_label = QLabel("Pi's Move: ?")
        self.computer_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.computer_score_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        self.computer_img = QLabel()
        pixmap = QPixmap(self.image_paths["rock"]).scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)
        self.computer_img.setPixmap(pixmap)
        self.computer_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.computer_img.setFixedSize(250, 250)
        self.computer_img.setStyleSheet("border: 2px solid red;")
        
        computer_layout.addWidget(self.computer_score_label)
        computer_layout.addWidget(self.computer_img)
        computer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add layouts to game layout
        game_layout.addLayout(player_layout)
        game_layout.addLayout(middle_layout)
        game_layout.addLayout(computer_layout)
        
        main_layout.addLayout(game_layout)
        
        # Result label
        self.result_label = QLabel("Make a gesture to start the game!")
        self.result_label.setObjectName("result_label")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main_layout.addWidget(self.result_label)
        
        # Timer display
        self.timer_label = QLabel("Time: Ready")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 16))
        main_layout.addWidget(self.timer_label)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: darkorange;
            }
        """)
        self.start_button.clicked.connect(self.start_game)
        
        # Results button
        self.results_button = QPushButton("Show Results")
        self.results_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9900;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: #ffcc00;
            }
        """)
        self.results_button.clicked.connect(self.show_results)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addSpacing(20)
        buttons_layout.addWidget(self.results_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        # Footer with winner announcement
        self.winner_label = QLabel("")
        self.winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.winner_label.setStyleSheet("color: #32CD32;")  # Light green
        main_layout.addWidget(self.winner_label)
        
        # Game state
        self.player_score = 0
        self.computer_score = 0
        self.player_gesture = None
        self.game_history = []
        
        # Timer setup
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_timer)
        self.time_left = 3

    def show_actions_menu(self):
        """Display the actions menu"""
        actions_menu = QMenu(self)
        actions_menu.setStyleSheet("""
            QMenu {
                background-color: #2c1584;
                color: white;
                border: 1px solid #888;
            }
            QMenu::item {
                background-color: transparent;
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #ff9900;
                color: black;
            }
        """)
        
        # Add menu items
        ai_info_action = actions_menu.addAction("Show AI Info")
        ai_info_action.triggered.connect(self.show_ai_info)
        
        # Find the actions button
        sender = self.sender()
        
        # Show the menu at the button position
        if sender:
            actions_menu.exec(sender.mapToGlobal(QPoint(0, sender.height())))

    def show_ai_info(self):
        """Show information about the AI"""
        QMessageBox.information(self, "AI Information", 
                              "This game uses computer vision techniques to recognize your hand gestures.\n\n"
                              "1. Show your hand in the green box\n"
                              "2. Make a gesture (rock, paper, or scissors)\n"
                              "3. The computer will randomly choose its move\n"
                              "4. Winner is determined by standard rock-paper-scissors rules")

    def start_game(self):
        self.result_label.setText("Get ready to show your gesture!")
        self.winner_label.setText("")
        self.player_gesture = None
        self.player_gesture_pixmap = None
        self.player_score_label.setText("Your Move: ?")
        self.computer_score_label.setText("Pi's Move: ?")
        
        self.time_left = 3
        self.timer_label.setText(f"Time: {self.time_left}")
        self.timer.start()

    def update_timer(self):
        self.time_left -= 1
        self.timer_label.setText(f"Time: {self.time_left}")
        
        if self.time_left <= 0:
            self.timer.stop()
            self.timer_label.setText("Time: Now!")
            self.play_round()

    def play_round(self):
        # Check if player gesture was detected
        if not self.player_gesture:
            # If camera is active but no gesture detected, notify user
            if self.camera_active:
                self.result_label.setText("No gesture detected! Using random choice.")
            
            # Use random gesture as fallback
            self.player_gesture = random.choice(self.choices)
            pixmap = QPixmap(self.image_paths[self.player_gesture]).scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)
            self.live_feed_label.setPixmap(pixmap)
        
        # For computer, choose randomly
        comp_choice = random.choice(self.choices)
        
        # Update display
        self.player_score_label.setText(f"Your Move: {self.player_gesture.capitalize()}")
        self.computer_score_label.setText(f"Pi's Move: {comp_choice.capitalize()}")
        
        # Show the computer's choice
        comp_pixmap = QPixmap(self.image_paths[comp_choice]).scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)
        self.animate_choice(comp_pixmap)
        
        # Determine winner
        result = self.determine_winner(comp_choice, self.player_gesture)
        
        # Update scores and display result
        winner = ""
        if "Pi" in result:
            self.computer_score += 1
            winner = "Pi"
        elif "You" in result:
            self.player_score += 1
            winner = "You"
        else:
            winner = "Tie"
            
        # Update result and winner display
        self.result_label.setText(f"Result: {result}")
        self.winner_label.setText(f"Winner: {winner}")
        
        # Update scoreboard
        self.scoreboard.setText(f"You: {self.player_score}  |  Pi: {self.computer_score}")
        
        # Show moves
        self.player_score_label.setText(f"Your Move: {self.player_gesture.capitalize()}")
        self.computer_score_label.setText(f"Pi's Move: {comp_choice.capitalize()}")
        
        # Add to game history
        self.game_history.append({
            "round": len(self.game_history) + 1,
            "player_move": self.player_gesture,
            "computer_move": comp_choice,
            "winner": winner,
            "player_score": self.player_score,
            "computer_score": self.computer_score
        })

    def animate_choice(self, new_pixmap: QPixmap):
        start_pos = self.computer_img.pos() - QPoint(100, 0)
        end_pos = self.computer_img.pos()

        self.computer_img.setPixmap(new_pixmap)
        self.computer_img.move(start_pos)

        anim = QPropertyAnimation(self.computer_img, QByteArray(b"pos"))
        anim.setDuration(500)
        anim.setStartValue(start_pos)
        anim.setEndValue(end_pos)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)
        anim.start()
        self.anim = anim

    def determine_winner(self, comp: str, player: str) -> str:
        beats = {
            "rock": "scissors",
            "scissors": "paper",
            "paper": "rock"
        }

        if comp == player:
            return "It's a Tie!"
        elif beats[comp] == player:
            return "Pi Wins!"
        else:
            return "You Win!"

    def show_results(self):
        """Show detailed game results in a message box"""
        if not self.game_history:
            QMessageBox.information(self, "Game Results", "No games played yet!")
            return
            
        results_text = "Game Results:\n\n"
        results_text += f"{'Round':<6} {'Your Move':<12} {'Pi Move':<12} {'Winner':<8}\n"
        results_text += "=" * 40 + "\n"
        
        for game in self.game_history:
            results_text += f"{game['round']:<6} {game['player_move'].capitalize():<12} {game['computer_move'].capitalize():<12} {game['winner']:<8}\n"
        
        results_text += "\n" + "=" * 40 + "\n"
        results_text += f"Final Score - You: {self.player_score}, Pi: {self.computer_score}\n"
        results_text += f"Overall Winner: {self.get_overall_winner()}"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Game Results")
        msg_box.setText(results_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #3b1d9e;
                color: white;
            }
            QLabel {
                color: white;
                font-family: monospace;
            }
            QPushButton {
                background-color: #ff9900;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
        """)
        msg_box.exec()
        
    def get_overall_winner(self):
        """Determine the overall winner of all games played"""
        if self.player_score > self.computer_score:
            return "You!"
        elif self.computer_score > self.player_score:
            return "Pi!"
        else:
            return "It's a tie!"

    def closeEvent(self, event):
        if hasattr(self, 'capture') and self.capture and self.capture.isOpened():
            self.capture.release()
        
        if hasattr(self, 'camera_timer') and self.camera_timer.isActive():
            self.camera_timer.stop()
            
        event.accept()

    def go_back_to_home(self):
        """Navigate back to the home page"""
        if self.parent_window and hasattr(self.parent_window, 'stack'):
            # Stop camera and timers before switching pages
            if hasattr(self, 'capture') and self.capture and self.capture.isOpened():
                self.capture.release()
            
            if hasattr(self, 'camera_timer') and self.camera_timer.isActive():
                self.camera_timer.stop()
                
            if self.timer.isActive():
                self.timer.stop()
                
            # Switch to the home page (index 0)
            self.parent_window.stack.setCurrentIndex(0)