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