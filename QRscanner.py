from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw

DO_RETURN = True


def detect_qr_codes_pyzbar(image_path):
    data = {}

    # Open the image
    img = Image.open(image_path)

    # Decode the QR codes
    decoded_objects = decode(img)

    if decoded_objects:
        for obj in decoded_objects:
            print(f"Type: {obj.type}")
            print(f"Data: {obj.data.decode('utf-8')}")
            print(f"Position: {obj.polygon}\n")

            data[obj.data.decode('utf-8')] = obj.polygon

            # Draw the bounding box around the QR code
            draw = ImageDraw.Draw(img)  # Create a drawing context
            draw.polygon(obj.polygon, outline="red")
    else:
        print("No QR Code detected")

    if DO_RETURN:
        return data


if __name__ == "__main__":
    DO_RETURN = False
    detect_qr_codes_pyzbar("Test-Images/20240810_144548.jpg")
