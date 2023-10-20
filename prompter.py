from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config, time, cookies

# tmp here
def wait_for_element(driver:WebDriver, by:By, selector:str, max_timeout:int = 120):
    try:
        element = WebDriverWait(driver, max_timeout).until(
            EC.visibility_of_element_located((by, selector))
        )
        return element
    except TimeoutError:
        return None

class Prompter:

    def __init__(self, driver:WebDriver):
        self.driver = driver
        self.cookies_present = cookies.check_cookies()

    def login(self):
        self.driver.get(config.OPENAI_LOGIN_URL)
        log_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="login-button"]')
        time.sleep(2)
        log_btn.click()
        
        login_input = wait_for_element(self.driver, By.ID, "username")
        if login_input:
            login_input.send_keys(config.OPENAI_LOGIN)
            login_input.send_keys(Keys.RETURN)
            time.sleep(0.5)
        
        pwd_input = wait_for_element(self.driver, By.ID, "password")
        if pwd_input:
            pwd_input.send_keys(config.OPENAI_PWD)
            time.sleep(0.5)

        continue_btn = wait_for_element(self.driver, By.CLASS_NAME, "_button-login-password")
        if continue_btn:
            continue_btn.click()
            time.sleep(2)
        cookies.save_cookies(self.driver)
        return
        