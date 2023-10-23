import undetected_chromedriver as uc
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import prompter , uvicorn, config, b64

app = FastAPI()

class VisionPrompt(BaseModel):
    b64str: str
    prompt: str

@app.post("/prompt")
async def handle_vision_prompt(vp: VisionPrompt, response: Response):
    try:
        options = uc.ChromeOptions()
        options.headless = False
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.notifications": 2
        })
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
        driver = uc.Chrome(options=options)
        p = prompter.Prompter(driver)
        conv_res = b64.b64_to_img(config.IMG_SAVE_PATH, vp.b64str)
        if conv_res == False:
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        res = p.vision_prompt(vp.prompt)
        return res
    finally:
        driver.quit()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=config.PORT)