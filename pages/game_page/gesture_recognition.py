import cv2
import numpy as np
import time
from collections import Counter

class GestureRecognizer:
    def __init__(self):
        # Constants for gesture recognition
        self.gestures = {
            'rock': 0,  # Fist - no fingers extended
            'paper': 1, # All fingers extended
            'scissors': 2, # Two fingers extended (index and middle)
            'lizard': 3, # Thumb and index finger forming mouth shape
            'spock': 4  # Vulcan salute - index, middle separated from ring, pinky
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
        
        # Performance metrics
        self.debug_mode = True  # Set to True to see accuracy metrics
        self.detection_start_time = None
        self.frame_count = 0
        self.fps_history = []
        self.confidence_scores = {'rock': 0, 'paper': 0, 'scissors': 0, 'lizard': 0, 'spock': 0}
        self.last_known_gesture = None
        self.gesture_stability_score = 0
        
    def preprocess_frame(self, frame):
        """Enhanced preprocessing for poor quality cameras"""
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
        """Recognize Rock, Paper, Scissors, Lizard, Spock gestures"""
        if contour is None:
            return None, frame
        
        # Create a convex hull around the contour
        hull = cv2.convexHull(contour)
        
        # Get contour and hull areas for features
        contour_area = cv2.contourArea(contour)
        hull_area = cv2.contourArea(hull)
        
        # Calculate contour complexity
        perimeter = cv2.arcLength(contour, True)
        complexity = (perimeter * perimeter) / (4 * np.pi * contour_area) if contour_area > 0 else 0
        
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
        
        # Analyze the defects for finger counting
        defect_points = []
        defect_angles = []
        defect_distances = []
        
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
                    angle_degrees = angle * 180 / np.pi
                    
                    # Store defect info
                    defect_points.append(far)
                    defect_angles.append(angle_degrees)
                    defect_distances.append(d / 256.0)  # Normalize the distance
                    
                    # More tolerance in angle detection (increased from 90 to 100 degrees)
                    if angle <= np.pi * 110/180:  # 110 degrees for better detection
                        finger_count += 1
                        cv2.circle(result_frame, far, 5, [0, 0, 255], -1)
                except:
                    continue
            
            # Always add 1 to finger_count (thumb is usually not detected as a defect)
            finger_count = min(finger_count + 1, 5)  # Cap at 5 fingers
            
            # Calculate additional features
            area_ratio = contour_area / max(hull_area, 1)  # Prevent division by zero
            
            # Enhanced gesture detection with convexity defect layout analysis
            gesture, confidence = self.advanced_gesture_detection(
                finger_count, defect_angles, defect_distances, defect_points, area_ratio, complexity
            )
            
            # Draw text on the frame
            cv2.putText(result_frame, f"Detected: {gesture}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show finger count for debugging
            cv2.putText(result_frame, f"Fingers: {finger_count}", (10, 90), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Track gesture stability
            if gesture:
                self.gesture_history.append(gesture)
                if len(self.gesture_history) > self.history_size:
                    self.gesture_history.pop(0)
                
                stable_gesture = self.get_stable_gesture()
                
                if stable_gesture:
                    cv2.putText(result_frame, f"Stable: {stable_gesture}", (10, 60), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                return stable_gesture or gesture, result_frame
                
        return self.get_stable_gesture(), result_frame
    
    def advanced_gesture_detection(self, finger_count, defect_angles, defect_distances, defect_points, area_ratio, complexity):
        """Enhanced gesture classification with multiple features"""
        
        # Initialize confidence scores for each gesture
        confidence = {
            'rock': 0.0,
            'paper': 0.0,
            'scissors': 0.0,
            'lizard': 0.0,
            'spock': 0.0
        }
        
        # -------------------- ROCK DETECTION --------------------
        # Rock: closed fist, few defects, compact shape
        if finger_count <= 1:
            confidence['rock'] = 0.7
            
            # Rock typically has a high area ratio (compact)
            if area_ratio > 0.85:
                confidence['rock'] += 0.2
                
            # Rock should have low complexity (simple shape)
            if complexity < 1.8:
                confidence['rock'] += 0.1
        
        # -------------------- PAPER DETECTION --------------------
        # Paper: open hand, many defects, spread shape
        if finger_count >= 4:
            confidence['paper'] = 0.6
            
            # Paper typically has a low-medium area ratio (spread fingers)
            if 0.6 < area_ratio < 0.85:
                confidence['paper'] += 0.2
                
            # Check for even spacing of defects (spread fingers)
            if len(defect_angles) >= 3:
                angles_std = np.std(defect_angles)
                if angles_std < 30:  # Low standard deviation means evenly spaced
                    confidence['paper'] += 0.2
        
        # -------------------- SCISSORS DETECTION --------------------
        # Scissors: two fingers extended (V shape)
        if 1 < finger_count < 4:
            # Check for large angle between the two fingers
            if len(defect_angles) > 0 and max(defect_angles) > 60:
                confidence['scissors'] = 0.6
                
                # Scissor typically has a medium area ratio
                if 0.65 < area_ratio < 0.8:
                    confidence['scissors'] += 0.2
                    
                # Two clear defect points
                if len(defect_points) == 2:
                    confidence['scissors'] += 0.2
        
        # -------------------- LIZARD DETECTION --------------------
        # Lizard: thumb and index finger extended like a mouth
        if 1 < finger_count < 3:
            # Lizard has specific area ratio (thumb + index makes a small area)
            if area_ratio > 0.8:
                confidence['lizard'] = 0.5
                
            # Lizard typically has a mouth-like shape (small opening)
            if len(defect_angles) == 1 and defect_angles[0] < 60:
                confidence['lizard'] += 0.3
                
            # Lizard has compact shape compared to scissors
            if complexity < 2.2:
                confidence['lizard'] += 0.2
        
        # -------------------- SPOCK DETECTION --------------------
        # Spock: Vulcan salute, 3-4 fingers in specific arrangement
        if 3 <= finger_count <= 4:
            # Specific arrangement of defects
            if len(defect_points) >= 3:
                confidence['spock'] = 0.5
                
                # Medium area ratio
                if 0.7 < area_ratio < 0.85:
                    confidence['spock'] += 0.2
                
                # Check for pattern of alternating defect angles (the V spacing of fingers)
                if len(defect_angles) >= 3:
                    # Sort angles and check if there's alternating pattern
                    sorted_angles = sorted(defect_angles)
                    if abs(sorted_angles[0] - sorted_angles[-1]) > 50:
                        confidence['spock'] += 0.3
        
        # Store confidence scores for display
        self.confidence_scores = confidence
        
        # Get the gesture with highest confidence
        max_gesture = max(confidence.items(), key=lambda x: x[1])
        
        # Return None if confidence is too low
        if max_gesture[1] < 0.4:
            return None, confidence
            
        # Calculate stability based on history
        if max_gesture[0] == self.last_known_gesture:
            self.gesture_stability_score = min(1.0, self.gesture_stability_score + 0.1)
        else:
            self.gesture_stability_score = max(0.0, self.gesture_stability_score - 0.2)
            
        self.last_known_gesture = max_gesture[0]
        return max_gesture[0], confidence
    
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
        if self.detection_start_time is None:
            self.detection_start_time = time.time()
        
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.detection_start_time
        
        # Calculate FPS every second
        if elapsed >= 1.0:
            fps = self.frame_count / elapsed
            self.fps_history.append(fps)
            if len(self.fps_history) > 10:
                self.fps_history.pop(0)
            self.frame_count = 0
            self.detection_start_time = current_time
        
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
        
        # Draw instructions for each gesture
        instructions = {
            'rock': "Make a fist for Rock",
            'paper': "Show open hand for Paper",
            'scissors': "Show index & middle fingers for Scissors",
            'lizard': "Make a hand puppet shape for Lizard",
            'spock': "Show Vulcan salute for Spock"
        }
        
        y_pos = roi_bottom + 30
        cv2.putText(frame, instructions.get(gesture, "Waiting for gesture..."), 
                   (roi_left, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Display performance metrics if in debug mode
        if self.debug_mode:
            # FPS
            avg_fps = sum(self.fps_history) / max(1, len(self.fps_history)) if self.fps_history else 0
            cv2.putText(frame, f"FPS: {avg_fps:.1f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Confidence scores
            y_offset = 60
            if gesture:
                # Draw a bar chart of confidence scores
                max_width = 150
                bar_height = 15
                for i, (gesture_name, score) in enumerate(sorted(self.confidence_scores.items(), key=lambda x: x[1], reverse=True)):
                    bar_width = int(score * max_width)
                    cv2.rectangle(frame, (10, y_offset + i*20), (10 + bar_width, y_offset + i*20 + bar_height), 
                                 (0, 255, 255), -1)
                    cv2.putText(frame, f"{gesture_name}: {score:.2f}", 
                               (10 + max_width + 10, y_offset + i*20 + bar_height), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Stability score
            cv2.putText(frame, f"Stability: {self.gesture_stability_score:.2f}", 
                       (10, y_offset + 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # History stats
            if self.gesture_history:
                counter = Counter(self.gesture_history)
                most_common = counter.most_common(1)[0]
                cv2.putText(frame, f"Most frequent: {most_common[0]} ({most_common[1]}/{len(self.gesture_history)})", 
                           (10, y_offset + 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
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