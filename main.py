from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import prompter, uvicorn, config, utils
from pathlib import Path
from typing import Optional, List
from utils import handle_img
from seleniumbase import Driver

app = FastAPI()

class VisionPrompt(BaseModel):
    b64_imgs: Optional[List[str]]
    url_imgs: Optional[List[str]]
    prompt: str

@app.post("/prompt")
async def handle_vision_prompt(vp: VisionPrompt):
    driver = Driver(
        browser="chrome",
        uc=True,
        headless2=True,
        incognito=True,
        agent=config.USER_AGENT,
        do_not_track=True,
        undetectable=True,
    )
    p = prompter.Prompter(driver, config.LOGIN_METHOD)
    try:
        if vp.url_imgs and vp.b64_imgs:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please provide either base64 strings or URLs, not both")
        if (vp.url_imgs and len(vp.url_imgs) > 4) or (vp.b64_imgs and len(vp.b64_imgs) > 4):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A maximum of 4 images can be provided.")

        # clear img cache before handling input imgs
        [f.unlink() for f in Path(config.IMG_CACHE_PATH).glob("*") if f.is_file()]

        if vp.url_imgs:
            for img_url in vp.url_imgs:
                img_res = handle_img(img_url)
                if not img_res:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to handle one of the inputs URL")
        elif vp.b64_imgs:
            for b64str in vp.b64_imgs:
                img_res = handle_img(b64str)
                if not img_res:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Failed to handle base64 image data")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No image data provided")
        return p.vision_prompt(vp.prompt)

    finally:
        driver.quit()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=config.PORT)