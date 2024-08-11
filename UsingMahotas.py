import mahotas as mh
import numpy as np
import cv2


GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FIXED_IMAGE_PATH = 'Manipulated-Scans/fixed_perspective_image.jpg'

# Step 1: Load the image
image_path = FIXED_IMAGE_PATH
image = mh.imread(image_path)

# Step 2: Convert to grayscale if necessary
if len(image.shape) == 3:
    image = mh.colors.rgb2gray(image)

# Step 3: Apply Gaussian filtering
blurred_image = mh.gaussian_filter(image, sigma=2)

# Step 4: Detect edges using Sobel filter
edges = mh.sobel(blurred_image)

# Step 5: Threshold the image
binary_edges = edges > edges.mean()

# Convert the binary edges to uint8 format (OpenCV requires this)
binary_edges = np.uint8(binary_edges * 255)

# Step 6: Find contours
contours, _ = cv2.findContours(binary_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Convert the original grayscale image to uint8
image_uint8 = np.uint8(image * 255)

# Step 7: Draw and display the contours
# Convert to BGR for color drawing
contour_image = cv2.cvtColor(image_uint8, cv2.COLOR_GRAY2BGR)

cv2.drawContours(contour_image, contours, -1, GREEN, 25)

mh.imsave("Manipulated-Scans/outline_scan.jpg", contour_image)
