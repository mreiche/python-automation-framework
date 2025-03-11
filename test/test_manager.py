import asyncio
import os
import shutil
from pathlib import Path
from urllib.parse import ParseResult

import inject
import pytest
from selenium.webdriver import ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver

from paf.common import Property, Size, Rect, Point
from paf.listener import WebDriverManagerListener
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.request import WebDriverRequest
from test import create_webdriver, finder
import paf.config

@pytest.fixture
def manager():
    yield inject.instance(WebDriverManager)


def test_manager_singleton(manager: WebDriverManager):
    manager2 = inject.instance(WebDriverManager)
    assert manager2 == manager


def test_take_screenshot(manager: WebDriverManager):
    create_webdriver()
    webdrivers = manager.webdrivers
    assert isinstance(webdrivers, list)

    for webdriver in webdrivers:
        path = manager.take_screenshot(webdriver)
        assert webdriver.session_id in path.name
        assert path.exists()

        path = manager.take_screenshot(webdriver, "test")
        assert webdriver.session_id not in path.name
        assert path.name == "test"
        assert path.exists()


def test_shutdown_by_session_key(manager: WebDriverManager):
    request = WebDriverRequest("test")
    create_webdriver(request)
    assert manager.has_webdriver(request)
    manager.shutdown_session(request)
    assert manager.has_webdriver(request.session_name) is False


def test_shutdown_unknown_session_fails(manager: WebDriverManager):
    with pytest.raises(Exception) as e:
        manager.shutdown_session("unknown")

    assert "Unknown session: unknown" in e.value.args[0]


@pytest.mark.skipif(
    os.getenv("PAF_TEST_CONTAINER") == "1",
    reason="Doesn't work in container",
)
def test_take_screenshot_fails_read_only(monkeypatch, manager: WebDriverManager):
    monkeypatch.setenv(Property.PAF_SCREENSHOTS_DIR.name, "read-only-screenshots")
    dir = Path(Property.env(Property.PAF_SCREENSHOTS_DIR))
    dir.mkdir(parents=True, exist_ok=True)
    os.chmod(dir, 555)
    webdriver = create_webdriver()
    path = manager.take_screenshot(webdriver)
    assert path is None
    os.chmod(dir, 775)
    shutil.rmtree(dir)


def test_take_screenshot_fails_invalid_session(manager: WebDriverManager):
    webdriver = create_webdriver()
    manager.shutdown(webdriver)
    with pytest.raises(Exception):
        manager.take_screenshot(webdriver)


def test_empty_request(manager: WebDriverManager):
    webdriver = create_webdriver()
    assert isinstance(webdriver, WebDriver)
    assert manager.has_webdriver("test")


def test_given_chrome_options(manager: WebDriverManager):
    request = WebDriverRequest("chrome-with-options")
    request.browser = "chrome"
    request.options = ChromeOptions()
    webdriver = create_webdriver(request)
    assert request.browser in webdriver.name


def test_not_given_chrome_options(manager: WebDriverManager):
    request = WebDriverRequest("chrome-no-options")
    request.browser = "chrome"
    webdriver = create_webdriver(request)
    assert request.browser in webdriver.name


@pytest.mark.skipif(
    os.getenv("PAF_TEST_LOCAL_SELENIUM") != "1",
    reason="No local Selenium server running",
)
def test_remote_webdriver(monkeypatch):
    monkeypatch.setenv('PAF_SELENIUM_SERVER_URL', "http://127.0.0.1:4444")
    request = WebDriverRequest("remote")
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


def test_window_size_and_position(finder: FinderPage):
    request = WebDriverRequest("position")
    request.window_position = Point(30, 40)
    request.window_size = Size(1024, 768)
    webdriver = create_webdriver(request)
    window_rect = Rect.from_rect_dict(webdriver.get_window_rect())

    assert window_rect.origin.x == 30
    assert window_rect.origin.y == 40
    assert window_rect.size.width == 1024
    assert window_rect.size.height == 768


def test_window_maximize():
    request = WebDriverRequest("maximize")
    request.window_maximize = True
    webdriver = create_webdriver(request)
    window_rect = Rect.from_rect_dict(webdriver.get_window_rect())
    assert window_rect.origin.x >= 0
    assert window_rect.origin.y >= 0
    assert window_rect.size.width > 1
    assert window_rect.size.height > 1


def first_task():
    return inject.instance(WebDriverManager)


def second_task():
    return inject.instance(WebDriverManager)


@pytest.mark.asyncio
async def test_thread_singleton():
    tasks = [
        asyncio.to_thread(first_task),
        asyncio.to_thread(second_task)
    ]

    managers = await asyncio.gather(*tasks)
    assert managers[0] == managers[1]



def test_listener():

    class WebDriverManagerTestListener(WebDriverManagerListener):
        def __init__(self):
            self.close_called = False
            self.create_called = False
            self.closed_called = False
            self.introduce_called = False
            self.introduced_called = False

        def webdriver_close(self, webdriver: WebDriver):
            self.close_called = True
        def webdriver_create(self, webdriver: WebDriver):
            self.create_called = True
        def webdriver_introduce(self, webdriver: WebDriver):
            self.introduce_called = True
        def webdriver_introduced(self, webdriver: WebDriver):
            self.introduced_called = True
        def webdriver_closed(self, webdriver: WebDriver):
            self.closed_called = True


    def _inject(binder: inject.Binder):
        paf.config.inject(binder)
        binder.bind(WebDriverManagerListener, WebDriverManagerTestListener())

    inject.clear_and_configure(_inject)
    listener: WebDriverManagerTestListener = inject.instance(WebDriverManagerListener)
    assert isinstance(listener, WebDriverManagerListener)

    request = WebDriverRequest("listener")

    manager = inject.instance(WebDriverManager)
    assert listener.create_called == False
    assert listener.introduce_called == False
    assert listener.introduced_called == False
    manager.get_webdriver(request)
    assert listener.create_called == True
    assert listener.introduce_called == True
    assert listener.introduced_called == True

    listener.create_called = False
    listener.introduce_called = False
    listener.introduced_called = False
    manager.get_webdriver(request)
    assert listener.create_called == False
    assert listener.introduce_called == False
    assert listener.introduced_called == False

    assert listener.close_called == False
    assert listener.closed_called == False
    manager.shutdown_session(request)
    assert listener.close_called == True
    assert listener.closed_called == True

    listener.closed_called = False
    with pytest.raises(Exception, match="Unknown session: listener"):
        manager.shutdown_session(request)
    assert listener.closed_called == False

def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
