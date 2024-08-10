from PIL import Image, ImageDraw
import qrgenerator

width = 0
height = 0

PIXELS_PER_MM = 38
SQUARE_SIZE = PIXELS_PER_MM * 10
SQUARE_COLOR_1 = "blue"
SQUARE_COLOR_2 = "yellow"
BACKGROUND_COLOR = "white"


def add_corner_triangle(image_path, triangle_size=15):
    img = Image.open(image_path)

    draw = ImageDraw.Draw(img)

    top_left = [(0, 0), (triangle_size, 0), (0, triangle_size)]

    draw.polygon(top_left, fill=SQUARE_COLOR_1)

    img.save("final_image.png")


def place_qr_on_image(rect_image_path, qr_file_paths, qr_positions, output_image_path):
    # Open the base image (checkerboard pattern)
    base_img = Image.open(rect_image_path).convert("RGBA")

    # Open and resize the QR code images
    qr_images = [Image.open(qr_path).convert("RGBA") for qr_path in qr_file_paths]

    qr_size_px = int(PIXELS_PER_MM * 3)  # Define size for QR codes, adjust if necessary

    for qr_img, pos in zip(qr_images, qr_positions):
        qr_img = qr_img.resize((qr_size_px, qr_size_px))  # Resize QR code
        base_img.paste(qr_img, pos, qr_img)  # Place QR code on base image

    base_img.save(output_image_path)


def create_checkerboard(width_mm, height_mm, square_size_mm, output_path):
    # Convert mm to pixels (assuming 100 pixels per mm for simplicity)
    width_px = int(width_mm / 10 * PIXELS_PER_MM)
    height_px = int(height_mm / 10 * PIXELS_PER_MM)
    square_size_px = int(square_size_mm / 10 * PIXELS_PER_MM)

    print(width_px)
    print(height_px)
    print(square_size_px)

    # Create a blank white image
    checkerboard = Image.new('RGB', (width_px, height_px), color=SQUARE_COLOR_2)
    draw = ImageDraw.Draw(checkerboard)

    # Draw the checkerboard pattern
    for y in range(0, height_px, square_size_px):
        for x in range(0, width_px, square_size_px):
            if (x // square_size_px + y // square_size_px) % 2 == 0:
                draw.rectangle([x, y, x + square_size_px, y + square_size_px], fill=SQUARE_COLOR_1)

    checkerboard.save(output_path)


def create_background_image(width_mm, height_mm, square_size_mm, output_path):
    # Convert mm to pixels (assuming 100 pixels per mm for simplicity)
    width_px = int(width_mm / 10 * PIXELS_PER_MM)
    height_px = int(height_mm / 10 * PIXELS_PER_MM)
    square_size_px = int(square_size_mm / 10 * PIXELS_PER_MM)

    print(width_px)
    print(height_px)
    print(square_size_px)

    # Create a blank white image
    checkerboard = Image.new('RGB', (width_px, height_px), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(checkerboard)

    checkerboard.save(output_path)


def get_dimensions():
    global width, height

    width = int(input("Enter the width of the box (mm): "))
    height = int(input("Enter the height of the box (mm): "))

    # Send width and height to qr making function
    qrgenerator.make_qr_corners(width, height)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_dimensions()
    # create_checkerboard(width, height, 10, 'checkerboard.png')
    create_background_image(width, height, 10, "background.png")
    qr_paths = ['Corner1.png', 'Corner3.png', 'Corner2.png', 'Corner4.png']
    # Locates the corners of the image
    positions = [(0, 0), (0, int((height / 10 * PIXELS_PER_MM) - SQUARE_SIZE / (10 / 3))),
                 (int((width / 10 * PIXELS_PER_MM) - SQUARE_SIZE / (10 / 3)), 0),
                 (int((width / 10 * PIXELS_PER_MM) - SQUARE_SIZE / (10 / 3)),
                  int((height / 10 * PIXELS_PER_MM) - SQUARE_SIZE / (10 / 3)))]

    place_qr_on_image("background.png", qr_paths, positions, 'image_w_qrs.png')
    add_corner_triangle("image_w_qrs.png")
