import os
import shutil
from pathlib import Path

import inject
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from paf.common import Property
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest
from test import create_webdriver
from selenium.webdriver import ChromeOptions
from urllib.parse import ParseResult


@pytest.fixture
def manager():
    yield inject.instance(WebDriverManager)


def test_manager_singleton(manager: WebDriverManager):
    manager2 = inject.instance(WebDriverManager)
    assert manager2 == manager


def test_take_screenshot(manager: WebDriverManager):
    create_webdriver()
    for webdriver in manager.webdrivers:
        path = manager.take_screenshot(webdriver)
        assert path.exists()


def test_shutdown_by_session_key(manager: WebDriverManager):
    request = WebDriverRequest("test")
    create_webdriver(request)
    manager.shutdown_session(request.session)


def test_shutdown_unknown_session_fails(manager: WebDriverManager):
    with pytest.raises(Exception) as e:
        manager.shutdown_session("unknown")

    assert "Unknown session: unknown" in e.value.args[0]


@pytest.mark.skipif(
    os.getenv("PAF_TEST_CONTAINER") == "1",
    reason="Doesn't work in container",
)
def test_take_screenshot_fails(monkeypatch, manager: WebDriverManager):
    monkeypatch.setenv(Property.PAF_SCREENSHOTS_DIR.name, "read-only-screenshots")
    dir = Path(Property.env(Property.PAF_SCREENSHOTS_DIR))
    dir.mkdir(parents=True, exist_ok=True)
    os.chmod(dir, 555)
    webdriver = create_webdriver()
    path = manager.take_screenshot(webdriver)
    assert path is None
    os.chmod(dir, 775)
    shutil.rmtree(dir)


def test_empty_request(manager: WebDriverManager):
    request = WebDriverRequest("empty")
    webdriver = create_webdriver(request)
    assert isinstance(webdriver, WebDriver)


def test_given_chrome_options(manager: WebDriverManager):
    request = WebDriverRequest("chrome")
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


def test_unknown_browser_fails(manager: WebDriverManager):
    with pytest.raises(Exception) as e:
        request = WebDriverRequest("unknown")
        request.browser = "unknown"
        #request.browser_version = "999"
        manager.get_webdriver(request)

    assert "No browser specified" in e.value.args[0]


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
