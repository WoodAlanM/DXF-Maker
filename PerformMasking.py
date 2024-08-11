import cv2
import numpy as np


def exclude_corners(image, corner_size):
    height, width = image.shape[:2]

    # Create a mask initialized to 255 (white)
    mask = np.ones((height, width), dtype=np.uint8) * 255

    # Define the size of the corner square
    size = corner_size

    # Fill in the top-left, top-right, bottom-left, and bottom-right squares with 0 (black)
    mask[0:size, 0:size] = 0
    mask[0:size, -size:] = 0
    mask[-size:, 0:size] = 0
    mask[-size:, -size:] = 0

    return mask


def extract_object_outline(image_path, corner_size=330):
    # Read the image
    img = cv2.imread(image_path)

    # Check if the image was loaded correctly
    if img is None:
        print(f"Error: Unable to open image at {image_path}")
        return None, None

    # Create mask to exclude corners
    mask = exclude_corners(img, corner_size)

    # Convert the mask to 3 channels
    mask_3ch = cv2.merge([mask, mask, mask])

    # Apply the mask to the image
    masked_img = cv2.bitwise_and(img, mask_3ch)

    # Convert to grayscale
    gray_img = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve edge detection
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred_img, 50, 150)

    # Find contours on the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a copy of the original image to draw contours on
    outline = img.copy()

    # Draw the contours on the copied image in blue
    if contours:
        cv2.drawContours(outline, contours, -1, (255, 0, 0), 2)  # Blue color for the outline
    else:
        print("No contours found.")

    return outline, contours


def create_object_mask(image_path):
    # Read the image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to create a binary mask
    _, mask = cv2.threshold(gray_img, 240, 255, cv2.THRESH_BINARY_INV)

    # Ensure the mask is 8-bit single-channel
    mask = mask.astype(np.uint8)

    return mask


def apply_mask_to_grid(grid_image_path, mask):
    # Read the grid image
    grid_img = cv2.imread(grid_image_path)

    # Resize the mask if it doesn't match the grid image size
    if mask.shape[:2] != grid_img.shape[:2]:
        mask = cv2.resize(mask, (grid_img.shape[1], grid_img.shape[0]))

    # Apply the mask to the grid image
    masked_img = cv2.bitwise_and(grid_img, grid_img, mask=mask)

    return masked_img