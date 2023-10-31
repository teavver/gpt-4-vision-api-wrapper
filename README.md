# gpt4-vision-wrapper

Demo wrapper for gpt4-v via api

## 31.10.2023 Update

The current version **should** be stable and working (no support for headless mode for now). I've managed to fix the Cloudflare problem for now.
If you encounter any problems, please open an [Issue](https://github.com/teavver/gpt4-vision-api-wrapper/issues).

## About

This project was developed as a small service for my personal needs. While it was primarily designed for my specific use-case, I hope that it can be useful to others who might find it relevant for their purposes.

Until the official API is released, I am open to suggestions and will try to implement new features as and when needed.

## Contributions

Contributions are more than welcome. If you have any improvement ideas or bug fixes, feel free to submit a pull request.

## How to use

1) Install packages with `installer.py` (make sure you're running your shell with admin privileges)
2) Set up .env with `OPENAI_LOGIN` and `OPENAI_PWD` - required for first-time setup (save the session cookies to .pkl), this ensures faster future requests. If you prefer to import your session manually, make sure the file is called `cookies.pkl` and is in base directory.
3) Start the local Api (default port is `5100`)

## Examples

(POST): `localhost:{PORT}/prompt`  
Body:

```json
{
    "b64str": "image in b64 string",
    // OR
    "url": "url to image",
    "prompt": "the prompt bro"
}
```

cURL:

```bash
curl \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"url": "https://twpark.com/wp-content/uploads/2021/09/amara-1.jpeg", "prompt": "Describe this image"}' \
  http://localhost:5100/prompt
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