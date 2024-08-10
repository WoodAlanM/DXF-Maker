import cv2
import numpy as np
from QRscanner import detect_qr_codes_pyzbar
from PIL import Image


def perspective_transform(image_path, positions):
    image = cv2.imread(image_path)

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
    transformed_image = cv2.warpPerspective(image, matrix, (int(width), int(height)))

    return transformed_image


def detect_edges(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return edges

# Example usage


def find_contours(edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def get_corner_positions(image_path):
    qrData = detect_qr_codes_pyzbar(image_path)
    print(qrData)

    grid_width = 0
    grid_height = 0
    corner_positions = {
        "top-left": None,
        "top-right": None,
        "bottom-left": None,
        "bottom-right": None
    }

    # This gets the corners from each qr code, and also collects the
    # width and height from the original grid generation.
    for corner, polygon in qrData.items():
        # Find top left of image
        if "Corner1" in corner:
            string_list = corner.split("&")
            print(string_list)
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

    print("****************************************")
    print("top-left corner: " + str(corner_positions["top-left"]))
    print("top-right corner: " + str(corner_positions["top-right"]))
    print("bottom-left corner: " + str(corner_positions["bottom-left"]))
    print("bottom-right corner: " + str(corner_positions["bottom-right"]))
    print("****************************************")


    print("Grid width = " + str(grid_width))
    print("Grid height = " + str(grid_height))


if __name__ == "__main__":
    get_corner_positions("Test-Images/grid-with-pliers-200x100.jpg")

    # fixed_perspective_image = perspective_transform('Test-Images/grid-with-pliers-200x100.jpg', positions)
    # cv2.imwrite('Manipulated-Scans/fixed_perspective_image.jpg', fixed_perspective_image)
    # edges = detect_edges(fixed_perspective_image)
    # cv2.imwrite('Manipulated-Scans/edges.jpg', edges)
    # contours = find_contours(edges)
    # cv2.drawContours(fixed_perspective_image, contours, -1, (0, 255, 0), 2)
    # cv2.imwrite('Manipulated-Scans/contours.jpg', fixed_perspective_image)
