import base64
from io import BytesIO

from PIL import Image


def Image_to_b64(img: Image):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
