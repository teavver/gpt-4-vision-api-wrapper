# gpt4-vision-wrapper

Demo wrapper for gpt4-v via api

# Project Status Notice

This project is just a shitty scrap. I do not have plans to maintain, upgrade, or offer support for it in the future. PRs are always welcome

# Usage

1) Install packages: `python installer.py`
2) Set up .env with `OPENAI_LOGIN` and `OPENAI_PWD`
3) Start the local Api

Request schema:
```json
{
    "b64str": "base64 encoded string of your image",
    "prompt": "the prompt bro"
}
```