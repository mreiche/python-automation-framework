import os

import inject
from selenium.webdriver import ChromeOptions

from paf.common import Size
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest


def create_webdriver(request: WebDriverRequest = None):
    manager = inject.instance(WebDriverManager)

    if not request:
        request = WebDriverRequest("test")

    if not request.browser:
        request.browser = "chrome"

    if os.getenv("PAF_TEST_HEADLESS") == "1":
        request.options = ChromeOptions()
        request.options.add_argument("--headless")
        if not request.window_size:
            request.window_size = Size(1920, 1080)

    if os.getenv("PAF_TEST_CONTAINER") == "1":
        request.options.add_argument("--disable-gpu")
        #request.options.add_argument("--remote-debugging-port=9222")  # this
        request.options.add_argument("--disable-dev-shm-usage")
        request.options.add_argument("--disable-extensions")
        request.options.add_argument("--no-sandbox")
        #request.options.add_argument("--disable-setuid-sandbox")
        request.options.add_argument("--disable-gpu-sandbox")

    return manager.get_webdriver(request)
