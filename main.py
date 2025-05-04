import cv2
import numpy as np
from src.inference import GestureClassifier
from src.feedback import FeedbackHandler
from src.ui_components import UIComponents
from src.preprocess import preprocess_frame
from game import GameEngine
from src.capture_page import CapturePage

classifier = GestureClassifier()
feedback = FeedbackHandler()
ui = UIComponents(classifier.categories)
game = GameEngine(mode='local')
capture_page = CapturePage(classifier.categories)

cap = cv2.VideoCapture(0)
cv2.namedWindow("Gesture App", cv2.WINDOW_NORMAL)

frames_buffer = []
prediction_result = []
show_feedback_ui = False
retrain_prompt = False
added_data_count = 0
last_game_result = (None, None, None)  # user, opponent, rule
last_outcome = ""
last_outcome_timer = 0

print("[INFO] Press SPACE to predict, F to give feedback, ESC to exit.")

def draw_controls_overlay(frame):
    lines = [
        "[SPACE] Capture Gesture    [F] Feedback Mode    [ESC] Exit",
        "[A] Add to Dataset         [R] Retrain via Capture",
        "[W/S] Select Gesture       [Y/N] Confirm Retrain",
        "[C] Open Capture Page"
    ]
    y_start = frame.shape[0] - 90
    for i, line in enumerate(lines):
        cv2.putText(frame, line, (10, y_start + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    return frame

while True:
    ret, frame = cap.read()
    if not ret:
        break

    original, _, processed = preprocess_frame(frame)
    key = cv2.waitKey(1) & 0xFF

    if key == 32 and not show_feedback_ui and not retrain_prompt:
        frames_buffer = []
        for _ in range(30):
            ret2, frame2 = cap.read()
            _, _, proc = preprocess_frame(frame2)
            frames_buffer.append(proc)
        prediction_result, _ = classifier.predict_with_buffer(frames_buffer)

        user_gesture = prediction_result[0][0]
        opponent_gesture = game.get_opponent_move()
        outcome, rule = game.decide_winner(user_gesture, opponent_gesture)
        last_game_result = (user_gesture, opponent_gesture, rule)
        last_outcome = outcome
        last_outcome_timer = 100

    if key == ord('f') and prediction_result:
        show_feedback_ui = True

    if show_feedback_ui:
        ui.handle_dropdown_input(key)

        if key == ord('a'):
            feedback.save_frames_to_class(frames_buffer, ui.get_selected_category())
            show_feedback_ui = False
            prediction_result = []
            added_data_count += 1
            if added_data_count >= 3:
                retrain_prompt = True

        elif key == ord('r'):
            feedback.launch_capture_mode(ui.get_selected_category())
            show_feedback_ui = False
            prediction_result = []

    if key == ord('c'):
        capture_page.run()
        continue

    if retrain_prompt:
        cv2.putText(original, "Retrain now? [Y/N]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        if key == ord('y'):
            feedback.trigger_retraining()
            retrain_prompt = False
            added_data_count = 0
        elif key == ord('n'):
            retrain_prompt = False

    display = original.copy()
    processed_preview = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    processed_preview = cv2.resize(processed_preview, (224, 224))

    if prediction_result:
        y_offset = 30
        for idx, (label, conf) in enumerate(prediction_result):
            text = f"{label}: {conf * 100:.2f}%"
            color = (0, 255, 0) if idx == 0 else (255, 255, 255)
            cv2.putText(display, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30

    if last_game_result[0]:
        summary_text = f"You: {last_game_result[0]} | Opponent: {last_game_result[1]}"
        rule_text = last_game_result[2]
        cv2.putText(display, summary_text, (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(display, rule_text, (10, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    if last_outcome_timer > 0:
        color = (0, 255, 0) if last_outcome == "User Wins" else (0, 0, 255) if last_outcome == "Opponent Wins" else (255, 255, 0)
        cv2.putText(display, last_outcome, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        last_outcome_timer -= 1

    if show_feedback_ui:
        display = ui.draw_dropdown(display)
        actions = [("Add to Dataset [A]", True), ("Retrain Gesture [R]", True)]
        display = ui.draw_buttons(display, actions)

    display = draw_controls_overlay(display)

    h1, w1, _ = display.shape
    h2, w2, _ = processed_preview.shape
    if h1 != h2:
        display = cv2.resize(display, (w1, h2))
    combined = np.hstack((display, processed_preview))

    cv2.imshow("Gesture App", combined)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
