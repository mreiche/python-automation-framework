import inject
import pytest
from selenium.webdriver import ChromeOptions

from paf.manager import WebDriverManager
from paf.request import WebDriverRequest
from test import create_webdriver


def test_detect_webdriver():
    request = WebDriverRequest("automated")
    request.browser = "chrome"
    webdriver = create_webdriver(request)
    result = webdriver.execute_script("return navigator.webdriver")
    assert result is True


@pytest.mark.skip(reason="Does not work in test image")
def test_hide_webdriver():
    # https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec
    request = WebDriverRequest("non-automated")
    request.browser = "chrome"
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    request.options = options
    webdriver = create_webdriver(request)
    webdriver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    result = webdriver.execute_script("return navigator.webdriver")
    assert result is False


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
