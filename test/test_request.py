from urllib.parse import ParseResult

import inject

from paf.manager import WebDriverManager
from paf.request import WebDriverRequest


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

def test_window_position(monkeypatch):
    monkeypatch.setenv('PAF_WINDOW_POSITION', '8x15')
    request = WebDriverRequest()
    assert request.window_position.x == 8
    assert request.window_position.y == 15

def test_window_maximize(monkeypatch):
    monkeypatch.setenv('PAF_WINDOW_MAXIMIZE', 'true')
    request = WebDriverRequest()
    assert request.window_maximize is True

def test_server_url(monkeypatch):
    monkeypatch.setenv('PAF_SELENIUM_SERVER_URL', "http://127.0.0.1:4444")
    request = WebDriverRequest("remote")
    request.browser = "chrome"
    assert isinstance(request.server_url, ParseResult)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
