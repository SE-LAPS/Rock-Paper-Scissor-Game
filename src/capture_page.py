import cv2
import os
from datetime import datetime
from src.preprocess import preprocess_frame
from src.ui_components import UIComponents

class CapturePage:
    def __init__(self, categories):
        self.categories = categories
        self.ui = UIComponents(categories)
        self.current_class = categories[0]
        self.console = ["Press SPACE to capture a frame", "Use W/S to change gesture", "ESC to return to game"]
        self.save_dir = "data"

    def save_frame(self, frame):
        class_path = os.path.join(self.save_dir, self.current_class)
        os.makedirs(class_path, exist_ok=True)
        filename = f"{self.current_class}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        filepath = os.path.join(class_path, filename)
        cv2.imwrite(filepath, frame)
        self.console.append(f"Saved: {filepath}")

    def run(self):
        cap = cv2.VideoCapture(0)
        cv2.namedWindow("Capture Page", cv2.WINDOW_NORMAL)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            original, _, processed = preprocess_frame(frame)
            self.current_class = self.ui.get_selected_category()

            # Display UI
            display = original.copy()
            self.ui.draw_dropdown(display, x=10, y=30)
            self.ui.draw_buttons(display, [("Back to Game [ESC]", True)], x=10, y_start=250)
            self.ui.draw_console_box(display, self.console)

            processed_preview = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            processed_preview = cv2.resize(processed_preview, (224, 224))

            # Combine view
            h1, w1, _ = display.shape
            h2, w2, _ = processed_preview.shape
            if h1 != h2:
                display = cv2.resize(display, (w1, h2))
            combined = cv2.hconcat([display, processed_preview])

            cv2.imshow("Capture Page", combined)
            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC
                break
            elif key == 32:
                self.save_frame(processed)
            else:
                self.ui.handle_dropdown_input(key)

        cap.release()
        cv2.destroyAllWindows()
