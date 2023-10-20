from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config, time, cookies

class Prompter:

    def __init__(self, driver:WebDriver):
        self.driver = driver
        self.cookies_present = cookies.check_cookies()

    def find_elem_with_timeout(self, by:By, selector:str, max_timeout:int = 120):
        try:
            element = WebDriverWait(self.driver, max_timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            return element
        except TimeoutError:
            return None

    # one-time login to save all .openai.com cookies
    def init_cookies(self):
        self.driver.get(config.OPENAI_LOGIN_URL)
        log_btn = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="login-button"]')
        time.sleep(1.0)
        log_btn.click()
        
        login_input = self.find_elem_with_timeout(By.ID, "username")
        if login_input:
            login_input.send_keys(config.OPENAI_LOGIN)
            login_input.send_keys(Keys.RETURN)
            time.sleep(0.5)
        
        pwd_input = self.find_elem_with_timeout(By.ID, "password")
        if pwd_input:
            pwd_input.send_keys(config.OPENAI_PWD)
            time.sleep(0.5)

        continue_btn = self.find_elem_with_timeout(By.CLASS_NAME, "_button-login-password")
        if continue_btn:
            continue_btn.click()
            time.sleep(1.0)
        cookies.save_cookies(self.driver)
        return
    
    def vision_prompt(self):
        self.driver.get(config.OPENAI_LOGIN_URL)
        time.sleep(0.5)
        
        if not self.cookies_present:
            print("[prompter] no cookies file found. initializing first time login")
            self.init_cookies()
        
        cookies.load_cookies(self.driver)
        self.driver.refresh()
        time.sleep(0.5)
        self.driver.get(config.OPENAI_GPT4_URL)
        time.sleep(2.0)

        # skip the welcome pop-up
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.RETURN).perform()
        time.sleep(0.5)

        # img_upload_btn = self.find_elem_with_timeout(By.CSS_SELECTOR, '[aria-label="Attach files"]')
        # time.sleep(1000)