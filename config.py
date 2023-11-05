import os
from dotenv import load_dotenv
from enum import Enum

# load env
load_dotenv()
if not os.getenv("OPENAI_LOGIN") or not os.getenv("OPENAI_PWD"):
    raise TypeError("[config] missing keys in .env. Check the docs or config.py")

class LoginMethod(Enum):
    OPENAI = 1
    GOOGLE = 2

# Login method
LOGIN_METHOD = LoginMethod['OPENAI'].value
# ___________________________^^^^______ Change this to 'GOOGLE' if you prefer
#                                       to log in using a Google account (first-time setup only)

# Credentials (for your selected login type)
OPENAI_LOGIN = os.getenv("OPENAI_LOGIN")
OPENAI_PWD = os.getenv("OPENAI_PWD")

# API
PORT = 5100

#  URLS
OPENAI_BASE_URL = "https://chat.openai.com"
OPENAI_LOGIN_URL = "https://chat.openai.com/auth/login"
OPENAI_GPT4_URL = "https://chat.openai.com/?model=gpt-4"

# Misc
IMG_BASE_FILENAME = "img"
IMG_CACHE_PATH = os.getcwd() + "/img_cache"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
