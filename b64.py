import base64, io, binascii
from PIL import Image

def b64_to_img(save_path:str, b64str: str) -> bool:
    if b64str.startswith("data:image"):
        b64str = b64str.split(",")[-1]
    try:
        imgdata = base64.b64decode(b64str)
    except (binascii.Error, ValueError) as e:
        print(f"Error decoding base64 string: {e}")
        return False

    image = Image.open(io.BytesIO(imgdata))
    image.save(save_path, 'PNG')
    return True