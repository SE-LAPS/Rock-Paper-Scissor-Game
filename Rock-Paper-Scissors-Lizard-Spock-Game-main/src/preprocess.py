import cv2
import numpy as np

def detect_skin_rgb(frame):
    frame = cv2.resize(frame, (400, 400))
    img = frame.astype(np.uint8)
    R = img[:, :, 2]
    G = img[:, :, 1]
    B = img[:, :, 0]

    # Rule 1: Uniform daylight
    rule1 = (
        (R > 95) & (G > 40) & (B > 20) &
        ((np.max(img, axis=2) - np.min(img, axis=2)) > 15) &
        (np.abs(R - G) > 15) & (R > G) & (R > B)
    )

    # Rule 2: Flash or side illumination
    rule2 = (
        (R > 220) & (G > 210) & (B > 170) &
        (np.abs(R - G) <= 15) & (B < R) & (B < G)
    )

    skin_mask = (rule1 | rule2).astype(np.uint8) * 255
    return frame, skin_mask

def clean_mask_with_morphology(mask):
    # Cross-shaped kernel 
    kernel_cross = np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ], dtype=np.uint8)

    kernel_square = np.array([
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ], dtype=np.uint8)

    # Custom dilation kernel 
    kernel_dilate = np.array([
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0]
    ], dtype=np.uint8)

    # Open (erosion → dilation)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_cross)

    dilated = cv2.dilate(opened, kernel_dilate, iterations=1)


    return dilated

def extract_largest_contour(mask):
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return mask, None

    largest = max(contours, key=cv2.contourArea)
    clean_mask = np.zeros_like(mask)
    cv2.drawContours(clean_mask, [largest], -1, 255, thickness=cv2.FILLED)
    return clean_mask, largest

def preprocess_frame(frame):
    frame, skin_mask = detect_skin_rgb(frame)
    cleaned = clean_mask_with_morphology(skin_mask)
    largest_only, _ = extract_largest_contour(cleaned)
    return frame, skin_mask, largest_only

def get_hand_contours(thresh_img, frame):
    contours, _ = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contoured = frame.copy()
    cv2.drawContours(contoured, contours, -1, (0, 255, 0), 2)
    return contoured
