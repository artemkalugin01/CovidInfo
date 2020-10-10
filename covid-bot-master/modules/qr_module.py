import datetime
import os
from pathlib import Path
import qrcode


# generating QR code
def get_content():
    file_path = f'output/qrcode{str(datetime.datetime.now().timestamp())}.png'
    img = qrcode.make('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    img.save(file_path)
    binary_file = Path(file_path).read_bytes()
    os.remove(file_path)
    return binary_file
