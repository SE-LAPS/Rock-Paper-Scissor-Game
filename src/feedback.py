import os
import cv2
from datetime import datetime
import subprocess

DATA_DIR = 'data'

class FeedbackHandler:
    def __init__(self, save_dir=DATA_DIR):
        self.save_dir = save_dir

    def save_frames_to_class(self, frames, class_name):
        class_path = os.path.join(self.save_dir, class_name)
        os.makedirs(class_path, exist_ok=True)

        for i, frame in enumerate(frames):
            filename = f"{class_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.png"
            filepath = os.path.join(class_path, filename)
            cv2.imwrite(filepath, frame)
        print(f"[INFO] Saved {len(frames)} frames to {class_path}")

    def launch_capture_mode(self, class_name):
        print(f"[INFO] Launching capture mode for class: {class_name}")
        subprocess.run(['python', 'src/capture.py', class_name])

    def trigger_retraining(self):
        print("[INFO] Starting retraining process...")
        subprocess.run(['python', 'src/train.py'])
