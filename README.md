# gpt4-vision-wrapper

Demo wrapper for gpt4-v via api

## Project Status Notice

This project is just a shitty scrap. I do not have plans to maintain, upgrade, or offer support for it in the future. PRs are always welcome

#### thx for the help, @damiancipolat

## Usage

1) Install packages: `python installer.py`
2) Set up .env with `OPENAI_LOGIN` and `OPENAI_PWD` - they are required only for the first-time setup to login and save the session cookies. this ensures faster future requests. If you prefer to import your session manually, make sure the file is called `cookies.pkl` and in base directory.
3) Start the local Api

Request schema: `POST`, `/prompt`
```json
{
    "b64str": "base64 encoded string of your image",
    "prompt": "the prompt bro"
}
```