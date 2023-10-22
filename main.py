import undetected_chromedriver as uc
from fastapi import FastAPI
from selenium import webdriver
import prompter 

options = uc.ChromeOptions() 
options.headless = False
driver = uc.Chrome(use_subprocess=True, options=options) 

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.post("/prompt")
# def handle_vision_prompt():

if __name__ == "__main__":
    p = prompter.Prompter(driver)
    p.vision_prompt("test_img.png", "Describe this image")
