import os

import inject
import pytest
from selenium.webdriver import ChromeOptions

from paf.common import Size
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.request import WebDriverRequest


@pytest.fixture()
def page_factory():
    yield inject.instance(PageFactory)

@pytest.fixture
def finder():
    page_factory = inject.instance(PageFactory)
    finder = page_factory.create_page(FinderPage, get_webdriver())
    yield finder


def get_webdriver(request: WebDriverRequest = None):
    manager = inject.instance(WebDriverManager)

    if not request:
        request = WebDriverRequest("test")

    if not request.browser:
        request.browser = "chrome"

    options = ChromeOptions()

    if os.getenv("PAF_TEST_HEADLESS") == "1":
        options.add_argument("--headless")
        if not request.window_size:
            request.window_size = Size(1920, 1080)

    #options.add_argument(f"--user-data-dir=/tmp/chromedriver-{request.session_name}")  # Strange behaviour in xdist
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_argument("--disable-extensions")

    if os.getenv("PAF_TEST_CONTAINER") == "1":
        options.add_argument("--disable-gpu")
        #options.add_argument("--remote-debugging-port=9222")  # this
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        #options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-gpu-sandbox")

    request.options = options
    return manager.get_webdriver(request)
