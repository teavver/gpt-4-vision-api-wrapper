import base64, io, binascii, requests
from datetime import datetime
from urllib.parse import urlparse
from PIL import Image

MODULE = "utils"

def is_valid_img_url(s: str) -> bool:
    parsed_url = urlparse(s)
    if not parsed_url.scheme or not parsed_url.netloc:
        return False
    supported_extensions = ['.webp', '.jpg', '.jpeg', '.png', '.gif', '.jfif', '.pjp', '.pjpeg']
    return any(parsed_url.path.lower().endswith(ext) for ext in supported_extensions)

def save_image_from_url(url: str, save_path: str) -> bool:
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except requests.RequestException as e:
        logger(MODULE, f"error fetching image from URL: {e}")
        return False

def handle_img(save_path: str, input_str: str) -> bool:
    if is_valid_img_url(input_str):
        return save_image_from_url(input_str, save_path)
    elif input_str.startswith("data:image"):
        input_str = input_str.split(",")[-1]
    try:
        imgdata = base64.b64decode(input_str)
    except (binascii.Error, ValueError) as e:
        logger(MODULE, f"error decoding base64 string: {e}")
        return False

    image = Image.open(io.BytesIO(imgdata))
    image.save(save_path, 'PNG')
    return True

def logger(module:str, msg:str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{timestamp} [{module}]: {msg}")