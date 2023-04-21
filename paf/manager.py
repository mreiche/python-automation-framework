import logging
import os
import threading
from pathlib import Path
from typing import Type, TypeVar, Iterable
from datetime import datetime

import inject
from selenium.webdriver import Chrome, Firefox, Edge, Safari
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from paf.common import Properties
from paf.request import WebDriverRequest
from paf.types import Consumer

OPTION = TypeVar("OPTION")

LOG = logging.getLogger(__name__)


class WebDriverManager:
    def __init__(self):
        self._session_driver_map: dict[str, WebDriver] = {}
        self._thread_driver_map: dict[int, WebDriver] = {}

    def _get_options(self, request: WebDriverRequest, options_class: Type[OPTION]) -> OPTION:
        options = request.options
        if not options:
            options = options_class()
        else:
            assert isinstance(options, options_class)
        return options

    def get_webdriver(self, request: WebDriverRequest = None) -> WebDriver:
        if not request:
            request = WebDriverRequest()

        session_key = request.session
        if session_key in self._session_driver_map:
            return self._session_driver_map[session_key]

        webdriver = None

        if request.browser in ["chrome", "chromium"]:
            options = self._get_options(request, ChromeOptions)
            webdriver = Chrome(options=options)
        elif request.browser in ["firefox"]:
            options = self._get_options(request, FirefoxOptions)
            webdriver = Firefox(options=options)
        elif request.browser in ["edge"]:
            webdriver = Edge()
        elif request.browser in ["safari"]:
            webdriver = Safari()

        if not webdriver:
            raise Exception("No browser specified")

        self._session_driver_map[session_key] = webdriver

        if request.window_size:
            LOG.info(f"Set window size: {request.window_size}")
            webdriver.set_window_rect(0, 0, request.window_size.width, request.window_size.height)

        return webdriver

    def shutdown_session(self, session_key):
        pass

    def shutdown(self, webdriver: WebDriver):
        webdriver.quit()
        webdrivers = list(self._session_driver_map.values())
        index = webdrivers.index(webdriver)

        session_keys = list(self._session_driver_map.keys())
        key = session_keys[index]
        self._session_driver_map.pop(key)

    def shutdown_all(self):
        for webdriver in list(self._session_driver_map.values()):
            self.shutdown(webdriver)

    def take_screenshot(self, webdriver: WebDriver) -> Path|None:
        dir = Path(os.getenv(Properties.PAF_SCREENSHOTS_DIR.name, Properties.PAF_SCREENSHOTS_DIR.value))
        file_name = f"{webdriver.title}-{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.png"
        dir.mkdir(parents=True, exist_ok=True)
        path = dir/file_name
        if webdriver.save_screenshot(dir / file_name):
            return path
        else:
            return None

    @property
    def webdrivers(self) -> Iterable[WebDriver]:
        return self._session_driver_map.values()


def inject_config(binder: inject.Binder):
    binder.bind(WebDriverManager, WebDriverManager())
