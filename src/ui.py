import cv2

class UIComponents:
    def __init__(self, categories):
        self.categories = categories
        self.selected_index = 0

    def draw_dropdown(self, frame, x=10, y=10):
        for i, category in enumerate(self.categories):
            color = (0, 255, 0) if i == self.selected_index else (255, 255, 255)
            cv2.putText(frame, category, (x, y + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame

    def handle_dropdown_input(self, key):
        if key == ord('w') and self.selected_index > 0:
            self.selected_index -= 1
        elif key == ord('s') and self.selected_index < len(self.categories) - 1:
            self.selected_index += 1

    def get_selected_category(self):
        return self.categories[self.selected_index]

    def draw_buttons(self, frame, actions, x=10, y_start=200):
        for i, (label, active) in enumerate(actions):
            color = (0, 255, 0) if active else (100, 100, 100)
            cv2.putText(frame, label, (x, y_start + i * 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        return frame