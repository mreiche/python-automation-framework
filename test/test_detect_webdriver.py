import inject
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


def test_hide_webdriver():
    request = WebDriverRequest("non-automated")
    request.browser = "chrome"
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    request.options = options
    webdriver = create_webdriver(request)
    result = webdriver.execute_script("return navigator.webdriver")
    assert result is False


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
