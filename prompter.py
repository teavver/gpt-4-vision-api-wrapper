from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config, time, cookies, os.path

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
        log_btn = self.find_elem_with_timeout(By.CSS_SELECTOR, '[data-testid="login-button"]')
        if log_btn:
            log_btn.click()
        
        login_input = self.find_elem_with_timeout(By.ID, "username")
        if login_input:
            login_input.send_keys(config.OPENAI_LOGIN)
            login_input.send_keys(Keys.RETURN)
            time.sleep(0.25)
        
        pwd_input = self.find_elem_with_timeout(By.ID, "password")
        if pwd_input:
            pwd_input.send_keys(config.OPENAI_PWD)
            time.sleep(0.25)

        continue_btn = self.find_elem_with_timeout(By.CLASS_NAME, "_button-login-password")
        if continue_btn:
            continue_btn.click()
        cookies.save_cookies(self.driver)
        return
    
    # img path is relative to current working directory (78)
    def vision_prompt(self, img_path:str, prompt:str):
        self.driver.get(config.OPENAI_LOGIN_URL)
        time.sleep(0.25)
        
        if not self.cookies_present:
            print("[prompter] no cookies file found. initializing first time login")
            self.init_cookies()
            time.sleep(2.5)
        else:
            cookies.load_cookies(self.driver)
            time.sleep(1)

        self.driver.refresh()
        self.driver.get(config.OPENAI_GPT4_URL)



        # close the welcome pop-up
        welcome_popup = self.find_elem_with_timeout(By.XPATH, '//button[.//div[text()="Okay, let’s go"]]')
        if welcome_popup:
            welcome_popup.click()
            time.sleep(1)

        # # # and the second one
        # search_with_imgs_popup = self.find_elem_with_timeout(By.XPATH, "//*[contains(@class, '-my-1') and contains(@class, '-mr-1') and contains(@class, 'p-1') and contains(@class, 'opacity-70')]")
        # if search_with_imgs_popup:
        #     search_with_imgs_popup.click()
        #     time.sleep(1)

        # file_inputs = self.driver.find_elements(By.XPATH, '//input[@type="file"]')
        # if len(file_inputs) > 0:
        #     full_img_path = os.path.join(os.getcwd() + "/" + img_path)
        #     file_inputs[0].send_keys(full_img_path)
        #     time.sleep(0.5)
            
        # prompt_textarea = self.find_elem_with_timeout(By.ID, "prompt-textarea")
        # if prompt_textarea:
        #     prompt_textarea.click()
        #     time.sleep(0.5)
        #     prompt_textarea.send_keys(prompt)
        #     time.sleep(2.5)
        #     prompt_textarea.send_keys(Keys.RETURN)

        time.sleep(1000)