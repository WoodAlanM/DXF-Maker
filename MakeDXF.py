import cv2
import numpy as np
from QRscanner import detect_qr_codes_pyzbar
from PIL import Image, ImageDraw
from UsingMahotas import *
from RemoveAndContour import *
import ezdxf

QR_CORNER_OFFSET = 32

corner_positions = {
        "top-left": [],
        "top-right": [],
        "bottom-left": [],
        "bottom-right": []
}


def perspective_transform(image_path, positions):
    image = cv2.imread(image_path)

    rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Assuming positions are in the correct order (top-left, top-right, bottom-right, bottom-left)
    pts1 = np.array([positions['top-left'], positions['top-right'],
                     positions['bottom-right'], positions['bottom-left']], dtype="float32")

    width = max(np.linalg.norm(pts1[0] - pts1[1]), np.linalg.norm(pts1[2] - pts1[3]))
    height = max(np.linalg.norm(pts1[0] - pts1[3]), np.linalg.norm(pts1[1] - pts1[2]))

    # Destination points for the perspective transformation
    pts2 = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype="float32")

    # Get the transformation matrix
    matrix = cv2.getPerspectiveTransform(pts1, pts2)

    # Apply the perspective transformation
    transformed_image = cv2.warpPerspective(rotated_image, matrix, (int(width), int(height)))

    return transformed_image


def detect_edges(image):
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # This is for ignoring black
    # mask = cv2.inRange(image, np.array([1, 1, 1]), np.array([255, 255, 255]))

    # These masks are for yellow and blue

    # Convert the image to the HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range for yellow color in HSV
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])

    # Define the range for blue color in HSV
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])

    # Create masks for yellow and blue colors
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Combine the masks
    combined_mask = cv2.bitwise_or(mask_yellow, mask_blue)

    # Invert the combined mask to exclude yellow and blue areas
    mask_inv = cv2.bitwise_not(combined_mask)

    masked_gray = cv2.bitwise_and(image, image, mask=mask_inv)

    edges = cv2.Canny(masked_gray, 50, 150)

    return edges


def find_contours(edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def get_corner_positions(image_path):
    qr_data = detect_qr_codes_pyzbar(image_path)

    grid_width = 0
    grid_height = 0

    # This gets the corners from each qr code, and also collects the
    # width and height from the original grid generation.
    for corner, polygon in qr_data.items():
        # Find top left of image
        if "Corner1" in corner:
            string_list = corner.split("&")
            for value in string_list:
                if "w=" in value:
                    value_list = value.split("=")
                    grid_width = int(value_list[1])
                elif "h=" in value:
                    value_list = value.split("=")
                    grid_height = value_list[1]
            # Get qr polygon coordinates
            qr_corners = polygon
            min_x = 0
            min_y = 0
            top_left_points = qr_corners
            left_most_points = []
            for i in range(2):
                lowest_x = 0
                for j in range(len(top_left_points)):
                    if j == 0:
                        min_x = qr_corners[0][0]
                        min_y = qr_corners[0][1]
                        continue
                    else:
                        if qr_corners[j][0] < min_x:
                            lowest_x = j
                            min_x = qr_corners[j][0]
                            min_y = qr_corners[j][1]
                left_most_points.append(qr_corners[lowest_x])
                del top_left_points[lowest_x]
            min_y = left_most_points[0][1]
            if left_most_points[1][1] < min_y:
                corner_positions["top-left"] = left_most_points[1]
            else:
                corner_positions["top-left"] = left_most_points[0]
            # Set top left position
            print(corner_positions["top-left"])
        # Find top right corner
        elif "Corner2" in corner:
            qr_corners = polygon
            max_x = 0
            min_y = 0
            top_right_points = qr_corners
            right_most_points = []
            for i in range(2):
                greatest_x = 0
                for j in range(len(top_right_points)):
                    if j == 0:
                        max_x = qr_corners[0][0]
                        min_y = qr_corners[0][1]
                        continue
                    else:
                        if qr_corners[j][0] > max_x:
                            greatest_x = j
                            max_x = qr_corners[j][0]
                            min_y = qr_corners[j][1]
                right_most_points.append(qr_corners[greatest_x])
                del top_right_points[greatest_x]
            min_y = right_most_points[0][1]
            if right_most_points[1][1] < min_y:
                corner_positions["top-right"] = right_most_points[1]
            else:
                corner_positions["top-right"] = right_most_points[0]
            print(corner_positions["top-right"])
        # Get bottom left corner
        elif "Corner3" in corner:
            qr_corners = polygon
            min_x = 0
            max_y = 0
            bottom_left_points = qr_corners
            left_most_points = []
            for i in range(2):
                lowest_x = 0
                for j in range(len(bottom_left_points)):
                    if j == 0:
                        min_x = qr_corners[0][0]
                        max_y = qr_corners[0][1]
                        continue
                    else:
                        if qr_corners[j][0] < min_x:
                            lowest_x = j
                            min_x = qr_corners[j][0]
                            max_y = qr_corners[j][1]
                left_most_points.append(qr_corners[lowest_x])
                del bottom_left_points[lowest_x]
            max_y = left_most_points[0][1]
            if left_most_points[1][1] > max_y:
                corner_positions["bottom-left"] = left_most_points[1]
            else:
                corner_positions["bottom-left"] = left_most_points[0]
            print(corner_positions["bottom-left"])
        elif "Corner4" in corner:
            qr_corners = polygon
            max_x = 0
            max_y = 0
            bottom_right_points = qr_corners
            right_most_points = []
            for i in range(2):
                greatest_x = 0
                for j in range(len(bottom_right_points)):
                    if j == 0:
                        max_x = qr_corners[0][0]
                        max_y = qr_corners[0][1]
                        continue
                    else:
                        if qr_corners[j][0] > max_x:
                            greatest_x = j
                            max_x = qr_corners[j][0]
                            max_y = qr_corners[j][1]
                right_most_points.append(qr_corners[greatest_x])
                del bottom_right_points[greatest_x]
            max_y = right_most_points[0][1]
            if right_most_points[1][1] > max_y:
                corner_positions["bottom-right"] = right_most_points[1]
            else:
                corner_positions["bottom-right"] = right_most_points[0]
            print(corner_positions["bottom-right"])

    # Corners turned out seemingly correct
    print("**********************************************")
    print("top-left corner: " + str(corner_positions["top-left"]))
    print("top-right corner: " + str(corner_positions["top-right"]))
    print("bottom-left corner: " + str(corner_positions["bottom-left"]))
    print("bottom-right corner: " + str(corner_positions["bottom-right"]))
    print("**********************************************")

    # Add 2.5 mm to each corner outward toward the outside
    # edge of the picture. This will compensate for the
    # Smaller size of the qr codes as compared to the squares
    # Fix top left corner
    top_left_corner = corner_positions["top-left"]
    top_left_x = top_left_corner[0]
    top_left_y = top_left_corner[1]
    top_left_x = top_left_x - QR_CORNER_OFFSET
    top_left_y = top_left_y - QR_CORNER_OFFSET
    corner_point = [top_left_x, top_left_y]
    corner_positions["top-left"] = corner_point

    top_right_corner = corner_positions["top-right"]
    top_right_x = top_right_corner[0]
    top_right_y = top_right_corner[1]
    top_right_x = top_right_x + QR_CORNER_OFFSET
    top_right_y = top_right_y - QR_CORNER_OFFSET
    corner_point = [top_right_x, top_right_y]
    corner_positions["top-right"] = corner_point

    bottom_left_corner = corner_positions["bottom-left"]
    bottom_left_x = bottom_left_corner[0]
    bottom_left_y = bottom_left_corner[1]
    bottom_left_x = bottom_left_x - QR_CORNER_OFFSET
    bottom_left_y = bottom_left_y + QR_CORNER_OFFSET
    corner_point = [bottom_left_x, bottom_left_y]
    corner_positions["bottom-left"] = corner_point

    bottom_right_corner = corner_positions["bottom-right"]
    bottom_right_x = bottom_right_corner[0]
    bottom_right_y = bottom_right_corner[1]
    bottom_right_x = bottom_right_x + QR_CORNER_OFFSET
    bottom_right_y = bottom_right_y + QR_CORNER_OFFSET
    corner_point = [bottom_right_x, bottom_right_y]
    corner_positions["bottom-right"] = corner_point

    print("**********************************************")
    print("top-left corner: " + str(corner_positions["top-left"]))
    print("top-right corner: " + str(corner_positions["top-right"]))
    print("bottom-left corner: " + str(corner_positions["bottom-left"]))
    print("bottom-right corner: " + str(corner_positions["bottom-right"]))
    print("**********************************************")

    # Test new positions
    # img = Image.open(image_path)
    #
    # draw = ImageDraw.Draw(img)
    #
    # points = [corner_positions["top-left"], corner_positions["top-right"],
    #           corner_positions["bottom-left"], corner_positions["bottom-right"]]
    #
    # radius = 20
    #
    # for point in points:
    #     left_up_point = (point[0] - radius, point[1] - radius)
    #     right_down_point = (point[0] + radius, point[1] + radius)
    #     draw.ellipse([left_up_point, right_down_point], fill='blue', outline='blue')
    #
    # img.save("Test-image-with-points.png")

    # Height and width of the grid was also retrieved correctly
    # print("Grid width = " + str(grid_width))
    # print("Grid height = " + str(grid_height))


def save_cv2_image(new_image_path, image):
    cv2.imwrite(new_image_path, image)


def convert_png_to_jpg(png_image_path, jpg_image_path):
    # Open the PNG image
    with Image.open(png_image_path) as img:
        # Convert image to RGB mode (JPG does not support alpha channel)
        rgb_img = img.convert("RGB")
        # Save the image as JPG
        rgb_img.save(jpg_image_path, format="JPEG")


def detect_object_contours(image_path):
    # Read the image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise and improve contour detection
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred_img, 50, 150)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw contours on a blank image
    contour_img = np.zeros_like(gray_img)
    cv2.drawContours(contour_img, contours, -1, (255), thickness=cv2.FILLED)

    return contours, contour_img


def make_corners_white(image_path, corner_size=330):
    # Load the image
    img = cv2.imread(image_path)

    # Get image dimensions
    height, width = img.shape[:2]

    # Create a mask initialized to zeros (black)
    mask = np.zeros((height, width, 3), dtype=np.uint8)

    # Define the size of the corner squares
    size = corner_size

    # Make the corners white
    mask[0:size, 0:size] = [255, 255, 255]  # Top-left corner
    mask[0:size, -size:] = [255, 255, 255]  # Top-right corner
    mask[-size:, 0:size] = [255, 255, 255]  # Bottom-left corner
    mask[-size:, -size:] = [255, 255, 255]  # Bottom-right corner

    # Apply the mask to the image to make corners white
    img_with_white_corners = cv2.addWeighted(img, 1, mask, 1, 0)

    return img_with_white_corners


def outline_object(image_path):
    # Load the image
    img = cv2.imread(image_path)

    # Convert to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to create a mask
    _, binary_img = cv2.threshold(gray_img, 240, 255, cv2.THRESH_BINARY_INV)

    # Find contours of the object
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an empty image to draw the contours (optional visualization)
    outline_img = np.ones_like(img) * 255  # White background
    cv2.drawContours(outline_img, contours, -1, (0, 0, 0), 2)  # Draw in black

    # cv2.imwrite("Manipulated-Scans/outlined_image.jpg", outline_img)

    return contours


def contours_to_dxf(contours, dxf_path, scale_factor=1.0):
    # Create a new DXF document
    doc = ezdxf.new(dxfversion="R2010")
    doc.header['$INSUNITS'] = 4  # 4 corresponds to millimeters
    msp = doc.modelspace()

    # Convert contours to polylines and add them to the DXF document
    for contour in contours:
        scaled_contour = [(point[0][0] * scale_factor, point[0][1] * scale_factor) for point in contour]
        polyline = msp.add_lwpolyline(scaled_contour)
        # polyline.is_closed = True  # Ensure the polyline is closed

    # Save the DXF file
    doc.saveas(dxf_path)


if __name__ == "__main__":
    # This gets the corner positions of the qr codes, then changes the
    # image perspective to fit a square image or rectangular.
    # get_corner_positions("Test-Images/20240810_144548.jpg")
    # fixed_perspective_image = perspective_transform('Test-Images/20240810_144548.jpg', corner_positions)
    # cv2.imwrite('Manipulated-Scans/fixed_perspective_image.jpg', fixed_perspective_image)

    # Starting to work here
    # image_path = 'Manipulated-Scans/fixed_perspective_image.jpg'
    # contour_image = draw_mahotas_contours(image_path)
    #
    # # Save or display the result
    # cv2.imwrite('Manipulated-Scans/mahotas_contour_image.jpg', contour_image)

    # whited_corners = make_corners_white("Manipulated-Scans/mahotas_contour_image.jpg")
    # cv2.imwrite("Manipulated-Scans/whited_filled_corners.jpg", whited_corners)

    # Get contours to make dxf file.
    outline_contours = outline_object("whited_corners.jpg")

    contours_to_dxf(outline_contours, "DXF-Output/pliers-dxf.dxf", 0.1)
