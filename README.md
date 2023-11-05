# gpt4-vision-wrapper

Demo wrapper for gpt4-v via api

## Update: November 6, 2023

Support for up to 4 image inputs added (4 is the upper limit set by OpenAI). Please check the [Examples](#examples) section for the updated schemas.

## Update: October 31, 2023

The current version **should** be stable and working (using the default config).  
If you encounter any problems, please open an [Issue](https://github.com/teavver/gpt4-vision-api-wrapper/issues).

## About

This project was developed as a small service for my personal needs. While it was primarily designed for my specific use-case, I hope that it can be useful to others who might find it relevant for their purposes.

Until the official API is released, I am open to suggestions and will try to implement new features as and when needed.

## Prerequisites

- Python >= 3.7
- OpenAI Account with GPT-Plus

## Contributions

Contributions are more than welcome. If you have any improvement ideas or bug fixes, feel free to submit a pull request.

## Config

Please modify the [config.py](https://github.com/teavver/gpt-4-vision-api-wrapper/blob/main/config.py) file to your needs. The default port is `5100`, and the default login method is `OPENAI`. You can also use a Google account for the first-time setup. Your credentials in the `.env` file should match your preferred login method.

## How to use

1) Install packages with `installer.py` or use `pip install -r requirements.txt` - **make sure you're running your shell with admin privileges**
2) Set up an `.env` file in the project root with `OPENAI_LOGIN` and `OPENAI_PWD` - required for first-time setup (save the session cookies to .pkl), this ensures faster future requests. If you prefer to import your session manually, make sure the file is called `cookies.pkl` and is in project root directory.
3) run `main.py` to start your local vision api (default port is `5100`).

## Examples

(POST): `localhost:{PORT}/prompt`

Body:

```json

{
    "b64_imgs": ["up to 4 images in b64-string format"],
    "prompt": "your prompt"
}

```

OR

```json
{
    "url_imgs": ["up to 4 image URLs", "second img", "etc..."],
    "prompt": "your prompt"
}
```

cURL:

```bash
curl \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"url_imgs": ["https://twpark.com/wp-content/uploads/2021/09/amara-1.jpeg"], "prompt": "Describe this image"}' \
  http://localhost:5100/prompt
```

You can use either `b64str` or `url`, not both. You can't mix up URLs and b64-encoded strings in the same request. Supported image formats (url):
- .webp
- .jpg
- .jpeg
- .png
- .gif
- .jfif
- .pjp
- .pjpeg