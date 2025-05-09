import cv2
import sys
import time
from pages.game_page.gesture_recognition import GestureRecognizer

def main():
    """Test the gesture recognition functionality"""
    print("Starting gesture recognition test...")
    
    # Initialize the gesture recognizer
    recognizer = GestureRecognizer()
    
    # Initialize the camera
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Error: Could not open camera.")
        return
    
    print("Camera opened successfully!")
    print("Press 'q' to quit, 'd' to toggle debug mode")
    
    # Main loop
    while True:
        # Read a frame from the camera
        ret, frame = capture.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break
        
        # Mirror the frame for more intuitive interaction
        frame = cv2.flip(frame, 1)
        
        # Process the frame for gesture recognition
        gesture, visualization = recognizer.process_frame(frame)
        
        # Display detected gesture
        if gesture:
            print(f"Detected gesture: {gesture}")
        
        # Display the frame
        cv2.imshow("Gesture Recognition Test", visualization)
        
        # Check for user input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Exiting...")
            break
        elif key == ord('d'):
            # Toggle debug mode
            recognizer.debug_mode = not recognizer.debug_mode
            print(f"Debug mode: {'ON' if recognizer.debug_mode else 'OFF'}")
    
    # Release resources
    capture.release()
    cv2.destroyAllWindows()
    print("Test completed.")

if __name__ == "__main__":
    main() 