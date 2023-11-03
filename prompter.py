from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import config, time, cookies, random
from utils import logger

MODULE = "prompter"

class GPTResponse:
    def __init__(self, locator):
        self.locator = locator
        self.last_known_text = None
        self.stable_count = 0

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if self.last_known_text == element.text:
            self.stable_count += 1
        else:
            self.stable_count = 0
            self.last_known_text = element.text

        if self.stable_count > 3:
            return element
        return False

class Prompter:

    def __init__(self, driver:WebDriver, login_method:int):
        self.driver = driver
        self.cookies_present = cookies.check_cookies()
        self.login_method = login_method

    def navigate_to_url(self, target_url:str, max_wait:int = 15):
        if self.driver.current_url != target_url:

            # October 29, 2023 Patch: https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1623#issuecomment-1777111043
            self.driver.execute_script(f"window.open('{target_url}', '_blank');")
            time.sleep(random.uniform(1.5, 3.5))

            last_tab = self.driver.window_handles[-1]
            self.driver.switch_to.window(last_tab)
            
            WebDriverWait(self.driver, max_wait).until(
                lambda d: d.current_url == target_url,
                logger(MODULE, f"failed to navigate to {target_url} in {max_wait} seconds.")
            )

    def check_for_error_message(self):
        error_message_locator = (By.XPATH, '//div[@class="mb-3 text-center text-xs" and text()="There was an error generating a response"]')
        try:
            error_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(error_message_locator)
            )
            return error_element.text
        except TimeoutException:
            return None

    def find_elem_with_timeout(self, by:By, selector:str, max_timeout:int = 10):
        try:
            element = WebDriverWait(self.driver, max_timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            time.sleep(random.uniform(1.25, 1.85))
            return element
        except TimeoutException:
            logger(MODULE, f"timeout - failed to find element `{selector}`")
            return None
        
    def login_and_navigate_to_gpt4(self):
        self.navigate_to_url(config.OPENAI_LOGIN_URL)
        if not self.cookies_present:
            logger(MODULE, f"no cookies file found. initializing first-time login. Method = {config.LoginMethod(self.login_method).name}")
            self.init_cookies()
        else:
            self.driver.delete_all_cookies()
            cookies.load_cookies(self.driver)
            time.sleep(1)
            self.driver.refresh()
            logger(MODULE, "cookies loaded. refreshed page.")
        self.navigate_to_url(config.OPENAI_GPT4_URL)
        return

    # one-time login to save cookies for future requests
    def init_cookies(self):
        log_btn = self.find_elem_with_timeout(By.CSS_SELECTOR, '[data-testid="login-button"]')
        if not log_btn: return
        logger(MODULE, "login btn click")
        log_btn.click()
        
        # Login using google account
        if config.LoginMethod(self.login_method).name == "GOOGLE":
            google_login_btn = self.find_elem_with_timeout(By.XPATH, "//button[contains(., 'Continue with Google')]")
            if not google_login_btn: return
            logger(MODULE, "google login btn click")
            google_login_btn.click()

            email_input = self.find_elem_with_timeout(By.XPATH, "//input[@type='email' and @name='identifier']")
            if not email_input: return
            logger(MODULE, "google email input")
            email_input.send_keys(config.OPENAI_LOGIN)

            next_btn = self.find_elem_with_timeout(By.XPATH, "//button[contains(., 'Next')]")
            if not next_btn: return
            next_btn.click()

            pwd_input = self.find_elem_with_timeout(By.XPATH, "//input[@type='password' and @name='Passwd']")
            if not pwd_input: return
            logger(MODULE, "google pwd input")
            pwd_input.send_keys(config.OPENAI_PWD)

            next_btn = self.find_elem_with_timeout(By.XPATH, "//button[contains(., 'Next')]")
            if not next_btn: return
            next_btn.click()

        # Login using OpenAI account
        else:
            login_input = self.find_elem_with_timeout(By.ID, "username")
            if not login_input: return
            login_input.send_keys(config.OPENAI_LOGIN)
            login_input.send_keys(Keys.RETURN)
            
            pwd_input = self.find_elem_with_timeout(By.ID, "password")
            if not pwd_input: return
            pwd_input.send_keys(config.OPENAI_PWD)

            continue_btn = self.find_elem_with_timeout(By.CSS_SELECTOR, 'button[data-action-button-primary="true"]')
            if not continue_btn: return
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-action-button-primary="true"]')))
            time.sleep(0.5) # important delay
            continue_btn.click()

        # Save cookies
        WebDriverWait(self.driver, 15).until(EC.url_contains('chat.openai.com'))
        cookies.save_cookies(self.driver)
        return
    
    def vision_prompt(self, prompt:str):

        self.login_and_navigate_to_gpt4()

        # close the welcome pop-up
        welcome_popup = self.find_elem_with_timeout(By.XPATH, '//button[.//div[text()="Okay, let’s go"]]')
        if not welcome_popup: return
        welcome_popup.click()

        # and the second one
        search_with_imgs_popup = self.find_elem_with_timeout(By.XPATH, "//*[contains(@class, '-my-1') and contains(@class, '-mr-1') and contains(@class, 'p-1') and contains(@class, 'opacity-70')]")
        if not search_with_imgs_popup: return
        search_with_imgs_popup.click()

        file_inputs = self.driver.find_elements(By.XPATH, '//input[@type="file"]')
        if len(file_inputs) == 0:
            return logger(MODULE, "file input not found")
        file_inputs[0].send_keys(config.IMG_SAVE_PATH)
            
        prompt_textarea = self.find_elem_with_timeout(By.ID, "prompt-textarea")
        if not prompt_textarea: return
        prompt_textarea.click()
        prompt_textarea.send_keys(prompt)

        send_btn_locator = (By.CSS_SELECTOR, 'button[data-testid="send-button"]')
        try:
            send_btn = WebDriverWait(self.driver, 45).until(
                EC.element_to_be_clickable(send_btn_locator)
            )
            send_btn.click()
        except TimeoutException:
            logger(MODULE, "timed out waiting for send btn")
        
        logger(MODULE, "prompt sent, waiting for response.")

        # await the full response and capture
        response_timeout = 240
        response_locator = (By.CSS_SELECTOR, '.markdown.prose')
        try:
            response = WebDriverWait(self.driver, response_timeout).until(
                GPTResponse(response_locator)
            )
            logger(MODULE, f"response: {response.text}")
        except TimeoutException:
            logger(MODULE, "timed out waiting for response")

        error_message = self.check_for_error_message()
        if error_message:
            return error_message

        return response.text