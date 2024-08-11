import cv2
import numpy as np


def exclude_corners(image, corner_size):
    height, width = image.shape[:2]
    mask = np.ones((height, width), dtype=np.uint8) * 255
    size = corner_size
    mask[0:size, 0:size] = 0
    mask[0:size, -size:] = 0
    mask[-size:, 0:size] = 0
    mask[-size:, -size:] = 0
    return mask


def create_object_mask(image_path, corner_size=330):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to open image at {image_path}")
        return None

    mask = exclude_corners(img, corner_size)
    mask_3ch = cv2.merge([mask, mask, mask])
    masked_img = cv2.bitwise_and(img, mask_3ch)

    gray_img = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    _, otsu_thresh = cv2.threshold(blurred_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = np.ones((5, 5), np.uint8)
    filled_img = cv2.morphologyEx(otsu_thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(filled_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return filled_img, contours


def remove_object(image_path, mask):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to open image at {image_path}")
        return None

    mask_3ch = cv2.merge([mask, mask, mask])
    removed_object_img = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(mask))

    return removed_object_img


def extract_cleaned_outline(image_path, mask, contour_color=(255, 0, 0)):
    removed_img = remove_object(image_path, mask)
    if removed_img is None:
        return None, None

    gray_img = cv2.cvtColor(removed_img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_img, (11, 11), 0)
    _, binary_img = cv2.threshold(blurred_img, 1, 255, cv2.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    filled_img = cv2.morphologyEx(binary_img, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(filled_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    outline = np.zeros_like(removed_img)
    if contours:
        cv2.drawContours(outline, contours, -1, contour_color, 2)
    else:
        print("No contours found.")

    return outline, contours

