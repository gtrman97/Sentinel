"""Page Object for the-internet.herokuapp.com/login."""

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LOGIN_URL = "https://the-internet.herokuapp.com/login"

USERNAME_INPUT = (By.ID, "username")
PASSWORD_INPUT = (By.ID, "password")
SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
FLASH_MESSAGE = (By.ID, "flash")


class LoginPage:
    """Encapsulates interactions with the login page."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout=10)

    def load(self) -> None:
        self.driver.get(LOGIN_URL)

    def login(self, username: str, password: str) -> None:
        self.wait.until(EC.presence_of_element_located(USERNAME_INPUT)).send_keys(username)
        self.driver.find_element(*PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*SUBMIT_BUTTON).click()

    def get_flash_message(self) -> str:
        element = self.wait.until(EC.visibility_of_element_located(FLASH_MESSAGE))
        return element.text