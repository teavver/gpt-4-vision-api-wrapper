import undetected_chromedriver as uc
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import prompter , uvicorn, config, b64

app = FastAPI()
options = uc.ChromeOptions() 
options.headless = False
driver = uc.Chrome(options=options)

class VisionPrompt(BaseModel):
    b64str: str
    prompt: str

@app.post("/prompt")
async def handle_vision_prompt(vp: VisionPrompt, response: Response):
    p = prompter.Prompter(driver)
    conv_res = b64.b64_to_img(config.IMG_SAVE_PATH, vp.b64str)
    if conv_res == False:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    res = p.vision_prompt(vp.prompt)
    return res

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=config.PORT)