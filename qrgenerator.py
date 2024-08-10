import qrcode


# This will make the qr codes for each corner
# The top right and the bottom left qr codes will also hold
# information about the partial squares on the grid
def make_qr_corners(width, height):
    qr_data = [('Corner1&w=' + str(width) + '&h=' + str(height)), 'Corner2', 'Corner3', 'Corner4']
    file_paths = ['Corner1.png', 'Corner2.png', 'Corner3.png', 'Corner4.png']

    for data, file_path in zip(qr_data, file_paths):
        img = qrcode.make(data)
        img.save(file_path)
