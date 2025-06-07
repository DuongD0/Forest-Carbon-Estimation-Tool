import cv2
import numpy as np

# Load the map image
img = cv2.imread('map.png')

if img is None:
    raise FileNotFoundError("map.png not found")

# Define the color range (e.g., green areas in BGR format)
lower_color = np.array([0, 100, 0])    # Dark green
upper_color = np.array([100, 255, 100])  # Light green

# Create a mask for the selected color
mask = cv2.inRange(img, lower_color, upper_color)

# Count pixels
colored_pixels = cv2.countNonZero(mask)

# Define scale (e.g., each pixel = 10 meters)
scale_factor = 10  # meters

# Convert pixels to real-world area
pixel_area = colored_pixels * (scale_factor ** 2)
print(f"Total area: {pixel_area} m²")
