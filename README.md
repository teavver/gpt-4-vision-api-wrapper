# gpt4-vision-wrapper

Demo wrapper for gpt4-v via api

## Project Status Notice

This project is just a shitty scrap. I do not have plans to maintain, upgrade, or offer support for it in the future. PRs are always welcome

#### thx for the help, @damiancipolat

## Usage

1) Install packages with `python installer.py`
2) Set up .env with `OPENAI_LOGIN` and `OPENAI_PWD` - required for first-time setup (save the session cookies to .pkl), this ensures faster future requests. If you prefer to import your session manually, make sure the file is called `cookies.pkl` and is in base directory.
3) Start the local Api

Request schema: `POST`, `/prompt`
```json
{
    "b64str": "image in b64 string",
    // OR
    "url": "url to image",
    "prompt": "the prompt bro"
}
```

You can use either b64str or url, not both. Supported image formats (url):
- .webp
- .jpg
- .jpeg
- .png
- .gif
- .jfif
- .pjp
- .pjpeg