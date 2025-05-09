import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_lizard_image():
    """Create a stylized image for the Lizard hand gesture"""
    # Create a blank image with transparent background
    width, height = 500, 500
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Create drawing context
    draw = ImageDraw.Draw(image)
    
    # Draw a hand silhouette for Lizard gesture
    # For Lizard: thumb and index finger extended in a mouth/puppet shape
    
    # Base palm - light purple color
    base_color = (150, 100, 200, 230)
    shadow_color = (100, 50, 150, 230)
    
    # Draw the palm
    palm_points = [(200, 350), (300, 350), (330, 250), (200, 250)]
    draw.polygon(palm_points, fill=base_color)
    
    # Draw thumb
    thumb_points = [(200, 250), (160, 200), (140, 150), (180, 180), (200, 250)]
    draw.polygon(thumb_points, fill=base_color)
    
    # Draw index finger
    index_points = [(240, 250), (230, 170), (240, 130), (260, 170), (240, 250)]
    draw.polygon(index_points, fill=base_color)
    
    # Draw middle finger (folded)
    middle_points = [(260, 250), (270, 220), (280, 230), (270, 250)]
    draw.polygon(middle_points, fill=shadow_color)
    
    # Draw ring finger (folded)
    ring_points = [(290, 250), (300, 220), (310, 230), (300, 250)]
    draw.polygon(ring_points, fill=shadow_color)
    
    # Draw pinky (folded)
    pinky_points = [(310, 250), (320, 230), (330, 240), (320, 250)]
    draw.polygon(pinky_points, fill=shadow_color)
    
    # Add text label
    font = ImageFont.truetype("arial.ttf", 40)
    draw.text((180, 400), "LIZARD", fill=(255, 255, 255, 255), font=font)
    
    # Save the image
    os.makedirs("assets/images", exist_ok=True)
    image.save("assets/images/lizard.png")
    print("Lizard image created successfully!")
    return image

def create_spock_image():
    """Create a stylized image for the Spock hand gesture (Vulcan salute)"""
    # Create a blank image with transparent background
    width, height = 500, 500
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Create drawing context
    draw = ImageDraw.Draw(image)
    
    # Draw a hand silhouette for Spock gesture (Vulcan salute)
    # Index and middle finger form a V, ring and pinky form another V
    
    # Base palm - blue-green color
    base_color = (100, 180, 200, 230)
    shadow_color = (70, 130, 150, 230)
    
    # Draw the palm
    palm_points = [(200, 350), (300, 350), (330, 250), (200, 250)]
    draw.polygon(palm_points, fill=base_color)
    
    # Draw thumb
    thumb_points = [(200, 250), (160, 200), (140, 150), (180, 180), (200, 250)]
    draw.polygon(thumb_points, fill=base_color)
    
    # Draw index finger
    index_points = [(220, 250), (210, 170), (200, 100), (220, 100), (240, 170), (240, 250)]
    draw.polygon(index_points, fill=base_color)
    
    # Draw middle finger
    middle_points = [(250, 250), (250, 170), (240, 100), (260, 100), (280, 170), (270, 250)]
    draw.polygon(middle_points, fill=base_color)
    
    # Draw ring finger
    ring_points = [(280, 250), (290, 170), (280, 100), (300, 100), (310, 170), (300, 250)]
    draw.polygon(ring_points, fill=base_color)
    
    # Draw pinky
    pinky_points = [(310, 250), (320, 180), (310, 120), (330, 120), (340, 180), (330, 250)]
    draw.polygon(pinky_points, fill=base_color)
    
    # Add text label
    font = ImageFont.truetype("arial.ttf", 40)
    draw.text((180, 400), "SPOCK", fill=(255, 255, 255, 255), font=font)
    
    # Save the image
    os.makedirs("assets/images", exist_ok=True)
    image.save("assets/images/spock.png")
    print("Spock image created successfully!")
    return image

if __name__ == "__main__":
    # Create both images
    lizard_img = create_lizard_image()
    spock_img = create_spock_image()
    
    # Display confirmation
    print("Gesture images created and saved to assets/images/") 