# process/camera_manager.py

import cv2

class CameraManager:
    _instance = None

    def __init__(self):
        self.capture = None
        self.user_count = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CameraManager()
        return cls._instance

    def acquire_camera(self):
        self.user_count += 1
        if self.capture is None or not self.capture.isOpened():
            self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        return self.capture

    def release_camera(self):
        self.user_count = max(0, self.user_count - 1)
        if self.user_count == 0 and self.capture:
            self.capture.release()
            self.capture = None
