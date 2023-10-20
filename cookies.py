import pickle, os.path
from selenium.webdriver.remote.webdriver import WebDriver

COOKIES_FILENAME = "cookies.pkl"

def check_cookies() -> bool:
    return os.path.isfile(COOKIES_FILENAME)


def save_cookies(driver:WebDriver, path:str = COOKIES_FILENAME):
    cookies = driver.get_cookies()
    pickle.dump(cookies, open(path, "wb"))


def load_cookies(driver:WebDriver, path:str = COOKIES_FILENAME):
    cookies = pickle.load(path, "rb")
    for cookie in cookies:
        cookie['domain'] = ".openai.com"
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(e)