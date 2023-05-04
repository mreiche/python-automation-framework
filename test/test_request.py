import os
from urllib.parse import ParseResult

import inject
import pytest
from selenium.webdriver import ChromeOptions

from paf.manager import WebDriverManager
from paf.request import WebDriverRequest
from test import create_webdriver


def test_browser(monkeypatch):
    monkeypatch.setenv('PAF_BROWSER_SETTING', 'firefox')
    request = WebDriverRequest()
    assert request.browser == "firefox"


def test_browser_version(monkeypatch):
    monkeypatch.setenv('PAF_BROWSER_SETTING', 'firefox:64')
    request = WebDriverRequest()
    assert request.browser == "firefox"
    assert request.browser_version == "64"

    request.browser_version = "99"
    assert request.browser_version == "99"


def test_window_size(monkeypatch):
    monkeypatch.setenv('PAF_WINDOW_SIZE', '1024x768')
    request = WebDriverRequest()
    assert request.window_size.width == 1024
    assert request.window_size.height == 768


def test_chrome_options():
    request = WebDriverRequest()
    request.browser = "chrome"
    request.options = ChromeOptions()
    webdriver = create_webdriver(request)
    assert webdriver.name == request.browser


@pytest.mark.skipif(
    os.getenv("PAF_TEST_LOCAL_SELENIUM") != "1",
    reason="Doesn't work in container",
)
def test_remote_webdriver(monkeypatch):
    server_url = "http://127.0.0.1:4444"
    monkeypatch.setenv('PAF_SELENIUM_SERVER_URL', server_url)
    request = WebDriverRequest()
    request.browser = "chrome"
    request.options = ChromeOptions()
    assert isinstance(request.server_url, ParseResult)
    webdriver = create_webdriver(request)
    assert webdriver.name == request.browser


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
