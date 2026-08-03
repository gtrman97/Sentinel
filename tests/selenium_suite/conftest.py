"""Shared pytest fixtures for the Selenium suite."""

from collections.abc import Iterator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver


@pytest.fixture
def driver() -> Iterator[WebDriver]:
    """Provide a fresh Chrome driver for each test, quitting it afterward."""
    chrome_driver = webdriver.Chrome()
    chrome_driver.implicitly_wait(0)  # we use explicit waits instead, never implicit
    yield chrome_driver
    chrome_driver.quit()