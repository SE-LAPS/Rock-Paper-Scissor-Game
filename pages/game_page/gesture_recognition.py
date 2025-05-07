import cv2
import numpy as np
import time

class GestureRecognizer:
    def __init__(self):
        # Constants for gesture recognition
        self.gestures = {
            'rock': 0,
            'paper': 1, 
            'scissors': 2
        }
        # Initialize background subtractor with relaxed parameters
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=25, detectShadows=False)
        self.kernel = np.ones((7, 7), np.uint8)  # Larger kernel for more aggressive morphology
        self.last_gesture = None
        self.countdown_active = False
        self.countdown_start = 0
        # Gesture stability tracking
        self.gesture_history = []
        self.history_size = 5
        
    def preprocess_frame(self, frame):
        """Enhanced preprocessing for poor quality cameras"""
        # Resize for better processing (optional, can help with poor cameras)
        # frame = cv2.resize(frame, (320, 240))
        
        # Apply bilateral filter to reduce noise while preserving edges
        filtered = cv2.bilateralFilter(frame, 9, 75, 75)
        
        # Increase contrast
        lab = cv2.cvtColor(filtered, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge((l, a, b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(blurred)
        
        # Remove shadows (gray pixels)
        _, thresh = cv2.threshold(fg_mask, 180, 255, cv2.THRESH_BINARY)
        
        # Perform morphological operations
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, self.kernel, iterations=1)
        dilated = cv2.dilate(opening, self.kernel, iterations=2)
        
        # Additional closing to connect nearby contours
        closed = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, self.kernel, iterations=2)
        
        return closed
    
    def find_contours(self, processed_frame):
        """Find contours in the processed frame with a lower area threshold"""
        contours, _ = cv2.findContours(processed_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Find the largest contour (assuming it's the hand)
            max_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(max_contour) > 500:  # Lower threshold for poor cameras
                return max_contour
        return None
    
    def recognize_gesture(self, contour, frame):
        """Recognize the gesture with more tolerance for errors"""
        if contour is None:
            return None, frame
        
        # Create a convex hull around the contour
        hull = cv2.convexHull(contour)
        
        # Find convexity defects - handle with more error tolerance
        try:
            # Simplify contour less aggressively
            epsilon = 0.005 * cv2.arcLength(contour, True)
            contour = cv2.approxPolyDP(contour, epsilon, True)
            hull_indices = cv2.convexHull(contour, returnPoints=False)
            
            # If hull_indices is empty or doesn't have enough points, return None
            if hull_indices is None or len(hull_indices) < 3:
                return self.get_stable_gesture(), frame
            
            defects = cv2.convexityDefects(contour, hull_indices)
        except:
            return self.get_stable_gesture(), frame
        
        # Count fingers (defects)
        finger_count = 0
        
        # Draw the contour and convexity defects
        result_frame = frame.copy()
        cv2.drawContours(result_frame, [contour], -1, (0, 255, 0), 2)
        
        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])
                
                # Calculate distance between points
                a = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = np.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = np.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                
                # Calculate angle with protection against division by zero
                try:
                    angle = np.arccos((b ** 2 + c ** 2 - a ** 2) / max(2 * b * c, 0.001))
                except:
                    continue
                
                # More tolerance in angle detection (increased from 90 to 100 degrees)
                if angle <= np.pi * 100/180:
                    finger_count += 1
                    cv2.circle(result_frame, far, 5, [0, 0, 255], -1)
            
            # Determine gesture based on finger count with lower precision requirements
            gesture = None
            
            # Always add 1 to finger_count (thumb)
            finger_count += 1
            
            if finger_count <= 2:
                gesture = 'rock'
            elif finger_count >= 4:
                gesture = 'paper'
            else:
                gesture = 'scissors'
            
            # Track gesture stability
            if gesture:
                self.gesture_history.append(gesture)
                if len(self.gesture_history) > self.history_size:
                    self.gesture_history.pop(0)
                
                stable_gesture = self.get_stable_gesture()
                
                # Draw text on the frame
                cv2.putText(result_frame, f"Detected: {gesture}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if stable_gesture:
                    cv2.putText(result_frame, f"Stable: {stable_gesture}", (10, 60), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                return stable_gesture or gesture, result_frame
                
        return self.get_stable_gesture(), result_frame
    
    def get_stable_gesture(self):
        """Return the most common gesture in history if it appears more than once"""
        if not self.gesture_history:
            return None
            
        # Count occurrences
        counts = {}
        for g in self.gesture_history:
            counts[g] = counts.get(g, 0) + 1
            
        # Find most common
        most_common = max(counts.items(), key=lambda x: x[1])
        
        # Only return if it appears multiple times
        if most_common[1] >= 2:
            return most_common[0]
        return None
        
    def process_frame(self, frame):
        """Process a frame and return recognized gesture and visualization"""
        if frame is None or frame.size == 0:
            return None, np.zeros((350, 350, 3), dtype=np.uint8)
            
        # Create a region of interest rectangle
        h, w = frame.shape[:2]
        
        # Make ROI dynamic based on frame size
        roi_size = min(w, h) - 20
        roi_left = (w - roi_size) // 2
        roi_top = (h - roi_size) // 2
        roi_right = roi_left + roi_size
        roi_bottom = roi_top + roi_size
        
        # Ensure ROI is within frame boundaries
        roi_left = max(0, roi_left)
        roi_top = max(0, roi_top)
        roi_right = min(w, roi_right)
        roi_bottom = min(h, roi_bottom)
        
        # Extract ROI
        roi = frame[roi_top:roi_bottom, roi_left:roi_right]
        
        if roi.size == 0:
            return None, frame
        
        # Add green rectangle
        cv2.rectangle(frame, (roi_left, roi_top), (roi_right, roi_bottom), (0, 255, 0), 2)
        
        # Process the ROI
        processed_roi = self.preprocess_frame(roi)
        contour = self.find_contours(processed_roi)
        
        gesture, visualization = self.recognize_gesture(contour, roi)
        
        # Add the visualization to the frame
        try:
            frame[roi_top:roi_bottom, roi_left:roi_right] = visualization
        except:
            # Fallback if sizes don't match
            resized_viz = cv2.resize(visualization, (roi_right - roi_left, roi_bottom - roi_top))
            frame[roi_top:roi_bottom, roi_left:roi_right] = resized_viz
        
        # Handle gesture detection with countdown
        current_time = time.time()
        
        if gesture and not self.countdown_active:
            self.countdown_active = True
            self.countdown_start = current_time
            self.last_gesture = gesture
        elif self.countdown_active and current_time - self.countdown_start > 1.0:
            self.countdown_active = False
            detected_gesture = self.last_gesture
            self.last_gesture = None
            return detected_gesture, frame
            
        return None, frame 