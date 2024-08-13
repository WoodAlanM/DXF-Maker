from PIL import Image, ImageDraw
import QRGenerator

width = 0
height = 0

PIXELS_PER_MM = .26458333333719
INFLATED_PIXELS_PER_MM = PIXELS_PER_MM * 14
QR_CODE_SIZE = 30
SQUARE_COLOR_1 = "blue"
SQUARE_COLOR_2 = "yellow"
BACKGROUND_COLOR = "white"


def add_corner_triangle(image_path, triangle_size=15):
    draw = ImageDraw.Draw(image_path)

    top_left = [(0, 0), (triangle_size, 0), (0, triangle_size)]

    draw.polygon(top_left, fill=SQUARE_COLOR_1)

    image_path.save("QR-Scanning-Images/final_image.png")


def place_qr_on_image(rect_image_path, qr_file_paths, qr_positions):
    # Open the base image (checkerboard pattern)
    base_img = rect_image_path.convert("RGBA")

    # Open and resize the QR code images
    qr_images = [Image.open(qr_path).convert("RGBA") for qr_path in qr_file_paths]

    qr_size_px = int(INFLATED_PIXELS_PER_MM * QR_CODE_SIZE)  # Define size for QR codes, adjust if necessary

    for qr_img, pos in zip(qr_images, qr_positions):
        qr_img = qr_img.resize((qr_size_px, qr_size_px))  # Resize QR code
        base_img.paste(qr_img, pos, qr_img)  # Place QR code on base image

    return base_img


# def create_checkerboard(width_mm, height_mm, square_size_mm, output_path):
#     # Convert mm to pixels (assuming 100 pixels per mm for simplicity)
#     width_px = int(width_mm / 10 * PIXELS_PER_MM)
#     height_px = int(height_mm / 10 * PIXELS_PER_MM)
#     square_size_px = int(square_size_mm / 10 * PIXELS_PER_MM)
#
#     print(width_px)
#     print(height_px)
#     print(square_size_px)
#
#     # Create a blank white image
#     checkerboard = Image.new('RGB', (width_px, height_px), color=SQUARE_COLOR_2)
#     draw = ImageDraw.Draw(checkerboard)
#
#     # Draw the checkerboard pattern
#     for y in range(0, height_px, square_size_px):
#         for x in range(0, width_px, square_size_px):
#             if (x // square_size_px + y // square_size_px) % 2 == 0:
#                 draw.rectangle([x, y, x + square_size_px, y + square_size_px], fill=SQUARE_COLOR_1)
#
#     checkerboard.save(output_path)


def create_background_image(width_mm, height_mm):
    # Convert mm to pixels (assuming 100 pixels per mm for simplicity)
    width_px = int(width_mm * INFLATED_PIXELS_PER_MM)
    height_px = int(height_mm * INFLATED_PIXELS_PER_MM)

    # Create a blank white image
    background = Image.new('RGB', (width_px, height_px), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(background)

    return background


def get_dimensions():
    global width, height

    width = int(input("Enter the width of the box (mm): "))
    height = int(input("Enter the height of the box (mm): "))

    # Send width and height to qr making function
    QRGenerator.make_qr_corners(width, height)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_dimensions()
    # create_checkerboard(width, height, 10, 'checkerboard.png')
    blank_background = create_background_image(width, height)
    qr_paths = ['Corner1.png', 'Corner3.png', 'Corner2.png', 'Corner4.png']
    # Locates the corners of the image
    positions = [(0, 0), (0, int((height * INFLATED_PIXELS_PER_MM) - (QR_CODE_SIZE * INFLATED_PIXELS_PER_MM))),
                 (int((width * INFLATED_PIXELS_PER_MM) - (QR_CODE_SIZE * INFLATED_PIXELS_PER_MM)), 0),
                 (int((width * INFLATED_PIXELS_PER_MM) - (QR_CODE_SIZE * INFLATED_PIXELS_PER_MM)),
                  int((height * INFLATED_PIXELS_PER_MM) - (QR_CODE_SIZE * INFLATED_PIXELS_PER_MM)))]

    background_with_qr_codes = place_qr_on_image(blank_background, qr_paths, positions)
    add_corner_triangle(background_with_qr_codes)
