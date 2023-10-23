from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import config, time, cookies

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

    def __init__(self, driver:WebDriver):
        self.driver = driver
        self.cookies_present = cookies.check_cookies()

    def navigate_to_url(self, target_url:str, max_wait:int = 15):
        if self.driver.current_url != target_url:
            self.driver.get(target_url)
            WebDriverWait(self.driver, max_wait).until(
                lambda d: d.current_url == target_url,
                f"[prompter] failed to navigate to {target_url} in {max_wait} seconds."
            )

    def find_elem_with_timeout(self, by:By, selector:str, max_timeout:int = 10):
        try:
            element = WebDriverWait(self.driver, max_timeout).until(
                # EC.presence_of_element_located((by, selector))
                EC.element_to_be_clickable((by, selector))
                # EC.visibility_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            print(f"[prompter] timeout - failed to find element `{selector}`")
            return None
        
    def login_and_navigate_to_gpt4(self):
        if not self.cookies_present:
            print("[prompter] no cookies file found. initializing first-time login.")
            self.init_cookies()
        else:
            cookies.load_cookies(self.driver)
            self.driver.refresh()
            print("[prompter] cookies loaded. refreshed page.")

        time.sleep(10000)

        self.navigate_to_url(config.OPENAI_BASE_URL)
        print('test')
        time.sleep(1.5)
        self.navigate_to_url(config.OPENAI_GPT4_URL)

    # one-time login to save cookies for future requests
    def init_cookies(self):
        self.driver.save_screenshot('debug_screenshot_cookies.png')
        self.driver.get(config.OPENAI_LOGIN_URL)
        log_btn = self.find_elem_with_timeout(By.CSS_SELECTOR, '[data-testid="login-button"]')
        if not log_btn: return
        log_btn.click()
        
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
        cookies.save_cookies(self.driver)
        return
    
    def vision_prompt(self, prompt:str):

        self.login_and_navigate_to_gpt4()

        time.sleep(5) # DEBUG
        self.driver.save_screenshot('debug_screenshot.png')

        # close the welcome pop-up
        welcome_popup = self.find_elem_with_timeout(By.XPATH, '//button[.//div[text()="Okay, let’s go"]]')
        if not welcome_popup: return
        welcome_popup.click()
        time.sleep(0.25)

        # and the second one
        search_with_imgs_popup = self.find_elem_with_timeout(By.XPATH, "//*[contains(@class, '-my-1') and contains(@class, '-mr-1') and contains(@class, 'p-1') and contains(@class, 'opacity-70')]")
        if not search_with_imgs_popup: return
        search_with_imgs_popup.click()
        time.sleep(0.25)

        file_inputs = self.driver.find_elements(By.XPATH, '//input[@type="file"]')
        if len(file_inputs) == 0:
            return print("[prompter] file input not found")
        file_inputs[0].send_keys(config.IMG_SAVE_PATH)
        time.sleep(0.25)
            
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
            print("[prompter] timed out waiting for send btn")

        # capture the response
        response_timeout = 240
        response_locator = (By.CSS_SELECTOR, '.markdown.prose')
        try:
            response = WebDriverWait(self.driver, response_timeout).until(
                GPTResponse(response_locator)
            )
            print(f"[prompter] response: {response.text}")
        except TimeoutException:
            print("[prompter] timed out waiting for response")

        return response.text