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


#@pytest.mark.skip(reason="Does not work in test image")
def test_hide_webdriver():
    # https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec
    request = WebDriverRequest("non-automated")
    request.browser = "chrome"
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    request.options = options
    webdriver = create_webdriver(request)
    webdriver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    webdriver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
    result = webdriver.execute_script("return navigator.webdriver")
    assert result is False


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
