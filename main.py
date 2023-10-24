from fastapi import FastAPI, Response, status, requests
from pydantic import BaseModel, validator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import prompter , uvicorn, config, utils
from typing import Optional

app = FastAPI()

class VisionPrompt(BaseModel):
    b64str: Optional[str]
    url: Optional[str]
    prompt: str

@validator('b64str', 'url', pre=True, always=True)
def check_input(cls, b64str, values):
        if not b64str and not values.get('url'):
            raise ValueError("Either b64 string or valid URL must be provided.")
        return b64str

@app.post("/prompt")
async def handle_vision_prompt(vp: VisionPrompt, response: Response):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.geolocation": 2,
        "profile.default_content_setting_values.notifications": 2
    })
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    p = prompter.Prompter(driver)

    try:
        if vp.url and vp.b64str:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Please provide either a b64 string or a URL, not both"}
        if vp.url:
            if not utils.is_valid_img_url(vp.url):
                response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                return {"error": "Invalid image URL"}
            if not utils.save_image_from_url(vp.url, config.IMG_SAVE_PATH):
                response.status_code = status.HTTP_400_BAD_REQUEST
                return {"error": "Failed to fetch image from URL"}
        elif vp.b64str:
            img_res = utils.handle_img(config.IMG_SAVE_PATH, vp.b64str)
            if img_res == False:
                response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                return {"error": "Failed to handle base64 image data"}
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "No image data provided"}

        return p.vision_prompt(vp.prompt)

    finally:
        driver.quit()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=config.PORT)