import os
import threading

import inject

from paf.common import Size
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest
from selenium.webdriver import ChromeOptions


def create_webdriver(request: WebDriverRequest = None):
    manager = inject.instance(WebDriverManager)
    if not request:
        request = WebDriverRequest(f"{__name__}{threading.get_ident()}")
    if not request.browser:
        request.browser = "chrome"
    if not request.window_size:
        request.window_size = Size(1920, 1080)
    if os.getenv("PAF_TEST_HEADLESS") == "1":
        request.options = ChromeOptions()
        request.options.add_argument("--headless")

    return manager.get_webdriver(request)
