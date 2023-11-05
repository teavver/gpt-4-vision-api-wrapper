from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import config, time, cookies, random, os
from utils import logger
from enum import Enum, auto

MODULE = "prompter"

class Action(Enum):
    Click = auto()
    Send_keys = auto()

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
        
    def find_elem_and_interact(self, elem_name: str, elem_action: Action, by: By, selector: str, input_keys: str = "", max_timeout: int = 15) -> WebElement:
        elem = self.find_elem_with_timeout(by, selector, max_timeout)
        if not elem:
            logger(MODULE, f"element {elem_name} not found")
            return None
        if elem_action == Action.Click:
            elem.click()
        elif elem_action == Action.Send_keys:
            elem.send_keys(input_keys)
        else:
            raise ValueError("Invalid action specified")
        return elem

    def find_elem_with_timeout(self, by:By, selector:str, max_timeout:int = 15) -> WebElement:
        try:
            element = WebDriverWait(self.driver, max_timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            time.sleep(random.uniform(0.75, 1.25))
            return element
        except Exception as e:
            logger(MODULE, f"timeout - unable to find element `{selector}`")
            # print(f"Exception: {e}")
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
        self.find_elem_and_interact("login_btn", Action.Click, By.CSS_SELECTOR, '[data-testid="login-button"]')
        
        # Login using google account
        if config.LoginMethod(self.login_method).name == "GOOGLE":

            self.find_elem_and_interact("google_login_btn", Action.Click, By.XPATH, "//button[contains(., 'Continue with Google')]")
            self.find_elem_and_interact("google_email_input", Action.Send_keys, By.XPATH, "//input[@type='email' and @name='identifier']", config.OPENAI_LOGIN)
            self.find_elem_and_interact("google_next_btn (1)", Action.Click, By.XPATH, "//button[contains(., 'Next')]")
            self.find_elem_and_interact("google_pwd_input", Action.Send_keys, By.XPATH, "//input[@type='password' and @name='Passwd']", config.OPENAI_PWD)
            self.find_elem_and_interact("google_next_btn (2)", Action.Click, By.XPATH, "//button[contains(., 'Next')]")

        # Login using OpenAI account
        else:

            self.find_elem_and_interact("openai_login_input", Action.Send_keys, By.ID, "username", config.OPENAI_LOGIN)
            self.find_elem_and_interact("openai_login_input", Action.Send_keys, By.ID, "username", Keys.RETURN)
            self.find_elem_and_interact("openai_login_pwd", Action.Send_keys, By.ID, "password", config.OPENAI_PWD)

            continue_btn = self.find_elem_with_timeout(By.CSS_SELECTOR, 'button[data-action-button-primary="true"]')
            if not continue_btn:
                logger(MODULE, "login continue btn not found")
                return
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-action-button-primary="true"]')))
            time.sleep(0.5) # important delay
            continue_btn.click()

        # Save cookies
        WebDriverWait(self.driver, 200).until(EC.url_contains('chat.openai.com'))
        cookies.save_cookies(self.driver)
        return
    
    def vision_prompt(self, prompt:str):

        self.login_and_navigate_to_gpt4()

        # close the welcome pop-up
        self.find_elem_and_interact("welcome_popup", Action.Click, By.XPATH, '//button[.//div[text()="Okay, let’s go"]]')

        # and the second one
        self.find_elem_and_interact("welcome_popup (2)", Action.Click, By.XPATH, "//*[contains(@class, '-my-1') and contains(@class, '-mr-1') and contains(@class, 'p-1') and contains(@class, 'opacity-70')]", "", 2)

        img_files = [f for f in os.listdir(config.IMG_CACHE_PATH) if f.startswith(config.IMG_BASE_FILENAME)]
        file_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
        )
        all_imgs = '\n'.join([os.path.join(config.IMG_CACHE_PATH, img_file) for img_file in img_files])
        file_input.send_keys(all_imgs)

        upload_timeout = 90
        WebDriverWait(self.driver, upload_timeout).until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, 'button[data-testid="send-button"]').get_attribute('disabled') is None or driver.find_element(By.CSS_SELECTOR, 'button[data-testid="send-button"]').get_attribute('disabled') == 'false'
        )
        logger(MODULE, "input imgs uploaded")

        logger(MODULE, "sending prompt")
        textarea = self.find_elem_and_interact("prompt_textarea", Action.Click, By.ID, "prompt-textarea")
        textarea.send_keys(prompt)

        upload_timeout = 90
        send_btn_locator = (By.CSS_SELECTOR, 'button[data-testid="send-button"]')
        try:
            send_btn = WebDriverWait(self.driver, upload_timeout).until(
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