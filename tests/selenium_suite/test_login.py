"""Tests for the login page.

Includes one deliberately flaky test (test_intentionally_flaky_demo) —
this exists solely to generate realistic messy JUnit XML data for Sentinel
to import and score later. It is NOT testing a real bug.
"""

import random

from selenium.webdriver.chrome.webdriver import WebDriver

from pages.login_page import LoginPage

VALID_USERNAME = "tomsmith"
VALID_PASSWORD = "SuperSecretPassword!"


def test_valid_login_succeeds(driver: WebDriver) -> None:
    """A real, stable test: valid credentials should log the user in."""
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login(VALID_USERNAME, VALID_PASSWORD)

    assert "You logged into a secure area" in login_page.get_flash_message()


def test_intentionally_flaky_demo(driver: WebDriver) -> None:
    """INTENTIONALLY FLAKY — for generating demo data only.

    Randomly passes or fails ~50% of the time, independent of the app under
    test. This exists so the importer/scoring logic has real status-flip
    data to work with. Delete once we have enough real run history, or keep
    permanently as a demo fixture — call to be made later.
    """
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login(VALID_USERNAME, VALID_PASSWORD)

    assert random.random() > 0.5, "Simulated flaky failure for demo purposes"