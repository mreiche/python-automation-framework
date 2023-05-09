from datetime import datetime
from pathlib import Path
from typing import Type, TypeVar, Iterable

import inject
from is_empty import empty
from selenium.webdriver import Chrome, Firefox, Edge, Safari, Remote, ChromeOptions, EdgeOptions, FirefoxOptions, WPEWebKitOptions
from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.remote.webdriver import WebDriver, BaseWebDriver
from paf.common import Property, Formatter
from paf.request import WebDriverRequest

OPTION = TypeVar("OPTION")


class WebDriverManager:
    def __init__(self):
        self._session_driver_map: dict[str, WebDriver] = {}
        self._thread_driver_map: dict[int, WebDriver] = {}

    def _get_options(self, request: WebDriverRequest, options_class: Type[OPTION]) -> OPTION:
        options = request.options
        if not options:
            options = options_class()
        else:
            assert isinstance(options, BaseOptions)

        return options

    def get_webdriver(self, request: WebDriverRequest) -> WebDriver:
        session_name = request.session_name
        if session_name in self._session_driver_map:
            return self._session_driver_map[session_name]

        webdriver = None
        webdriver_class: Type[BaseWebDriver] = None
        options: BaseOptions = None

        if request.browser in ["chrome"]:
            options = self._get_options(request, ChromeOptions)
            webdriver_class = Chrome
        elif request.browser in ["firefox"]:
            options = self._get_options(request, FirefoxOptions)
            webdriver_class = Firefox
        elif request.browser in ["edge"]:
            options = self._get_options(request, EdgeOptions)
            webdriver_class = Edge
        elif request.browser in ["safari"]:
            options = self._get_options(request, WPEWebKitOptions)
            webdriver_class = Safari
        else:
            raise Exception("No browser specified")

        if request.browser_version:
            options.set_capability("browserVersion", request.browser_version)
            # options.set_capability("platformName", "Windows XP")

        if request.server_url:
            webdriver = Remote(command_executor=request.server_url.geturl(), options=options)
        elif webdriver_class:
            webdriver = webdriver_class(options=options)

        self.introduce_webdriver(webdriver, request)

        return webdriver

    def introduce_webdriver(self, webdriver: WebDriver, request: WebDriverRequest):
        self._session_driver_map[request.session_name] = webdriver

        if request.window_size:
            #LOG.info(f"Set window size {request.window_size} on {webdriver.name}")
            webdriver.set_window_rect(0, 0, request.window_size.width, request.window_size.height)

    def has_webdriver(self, session_name):
        return session_name in self._session_driver_map

    def shutdown_session(self, session_name: str):
        if session_name in self._session_driver_map:
            self.shutdown(self._session_driver_map[session_name])
        else:
            raise Exception(f"Unknown session: {session_name}")

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

    def take_screenshot(self, webdriver: WebDriver) -> Path | None:
        dir = Path(Property.env(Property.PAF_SCREENSHOTS_DIR))
        title = webdriver.title
        if empty(title):
            title = webdriver.current_url

        formatter = inject.instance(Formatter)

        file_name = f"{title}-{formatter.datetime(datetime.now())}.png"
        dir.mkdir(parents=True, exist_ok=True)
        path = dir / file_name
        if webdriver.save_screenshot(dir / file_name):
            return path
        else:
            return None

    @property
    def webdrivers(self) -> Iterable[WebDriver]:
        return self._session_driver_map.values()


def inject_config(binder: inject.Binder):
    binder.bind(WebDriverManager, WebDriverManager())
