import base64, binascii, requests, time, random, config, os, glob
from datetime import datetime
from urllib.parse import urlparse
from selenium.webdriver.remote.webelement import WebElement

MODULE = "utils"

def is_valid_img_url(s: str) -> bool:
    parsed_url = urlparse(s)
    if not parsed_url.scheme or not parsed_url.netloc:
        return False
    supported_extensions = ['.webp', '.jpg', '.jpeg', '.png', '.gif', '.jfif', '.pjp', '.pjpeg']
    return any(parsed_url.path.lower().endswith(ext) for ext in supported_extensions)

def handle_img(input_str: str) -> bool:
    imgdata = None
    file_extension = 'png' # default file ext

    if is_valid_img_url(input_str):
        try:
            response = requests.get(input_str)
            response.raise_for_status()
            imgdata = response.content # file ext
            parsed_url = urlparse(input_str)
            file_extension = parsed_url.path.split('.')[-1]
        except requests.RequestException as e:
            logger(MODULE, f"error fetching image from URL: {e}")
            return False
    elif input_str.startswith("data:image"):
        input_str = input_str.split(",")[-1]
        try:
            imgdata = base64.b64decode(input_str)
            file_extension = input_str.split(';')[0].split('/')[-1] # file ext
        except (binascii.Error, ValueError) as e:
            logger(MODULE, f"error decoding base64 string: {e}")
            return False
    else:
        logger(MODULE, f"invalid input image format")
        return False

    idx = 0
    while True:
        new_filename = f"{config.IMG_BASE_FILENAME}{idx}.{file_extension}"
        new_save_path = os.path.join(config.IMG_CACHE_PATH, new_filename)
        if not os.path.exists(new_save_path):
            break
        idx += 1

    if imgdata:
        with open(new_save_path, 'wb') as f:
            f.write(imgdata)
    return True

def logger(module:str, msg:str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{timestamp} [{module}]: {msg}")