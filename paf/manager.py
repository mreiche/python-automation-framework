from datetime import datetime
from pathlib import Path
from typing import Type, TypeVar, List

import inject
import selenium
from is_empty import empty
from selenium.webdriver.common import service as webdriver_service
from selenium.webdriver.common.options import BaseOptions
from selenium.webdriver.remote.webdriver import WebDriver, BaseWebDriver

from paf.common import Property, Formatter
from paf.listener import WebDriverManagerListener
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
        session_name = request.name
        if session_name in self._session_driver_map:
            return self._session_driver_map[session_name]

        webdriver = None
        webdriver_class: Type[BaseWebDriver]
        options: BaseOptions
        service: webdriver_service.Service

        if request.browser in ["chrome"]:
            options = self._get_options(request, selenium.webdriver.ChromeOptions)
            service_class = selenium.webdriver.ChromeService
            webdriver_class = selenium.webdriver.Chrome
        elif request.browser in ["firefox"]:
            options = self._get_options(request, selenium.webdriver.FirefoxOptions)
            service_class = selenium.webdriver.FirefoxService
            webdriver_class = selenium.webdriver.Firefox
        elif request.browser in ["edge"]:
            options = self._get_options(request, selenium.webdriver.EdgeOptions)
            service_class = selenium.webdriver.EdgeService
            webdriver_class = selenium.webdriver.Edge
        elif request.browser in ["safari"]:
            options = self._get_options(request, selenium.webdriver.SafariOptions)
            service_class = selenium.webdriver.SafariService
            webdriver_class = selenium.webdriver.Safari
        else:
            raise Exception("No browser specified")

        if request.browser_version:
            options.set_capability("browserVersion", request.browser_version)

        listener = inject.instance(WebDriverManagerListener)
        if listener:
            listener.webdriver_create(request)

        if request.server_url:
            webdriver = selenium.webdriver.Remote(command_executor=request.server_url.geturl(), options=options)
        elif webdriver_class:
            service_options = {}
            if Property.PAF_DRIVER_PATH.value:
                service_options["executable_path"] = Property.PAF_DRIVER_PATH.value

            if Property.PAF_BINARY_PATH.value:
                options.binary_location = Property.PAF_BINARY_PATH.value

            service = service_class(**service_options)
            webdriver = webdriver_class(options=options, service=service)

        webdriver = self.introduce_webdriver(webdriver, request)

        return webdriver

    def introduce_webdriver(self, webdriver: WebDriver, request: WebDriverRequest) -> WebDriver:
        self.__set_request_name(webdriver, request)
        listener = inject.instance(WebDriverManagerListener)
        if listener:
            webdriver = listener.webdriver_introduce(webdriver)
            assert webdriver is not None

        self._session_driver_map[request.name] = webdriver

        if request.window_position:
            webdriver.set_window_position(request.window_position.x, request.window_position.y)

        if request.window_maximize:
            webdriver.maximize_window()

        elif request.window_size:
            webdriver.set_window_size(request.window_size.width, request.window_size.height)

        if listener:
            listener.webdriver_introduced(webdriver)

        return webdriver

    def __map_session_name(self, session_name_or_request: str | WebDriverRequest) -> str:
        if isinstance(session_name_or_request, WebDriverRequest):
            session_name_or_request = session_name_or_request.name
        return session_name_or_request

    def has_webdriver(self, session_name_or_request: str | WebDriverRequest):
        session_name = self.__map_session_name(session_name_or_request)
        return session_name in self._session_driver_map

    def shutdown_session(self, session_name_or_request: str | WebDriverRequest):
        session_name = self.__map_session_name(session_name_or_request)
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

    def take_screenshot(self, webdriver: WebDriver, file_name: str = None) -> Path | None:
        dir = Path(Property.env(Property.PAF_SCREENSHOTS_DIR))
        if empty(file_name):
            title = webdriver.title
            if empty(title):
                title = webdriver.current_url
            formatter = inject.instance(Formatter)
            file_name = f"{webdriver.session_id}-{title}-{formatter.datetime(datetime.now())}.png"

        dir.mkdir(parents=True, exist_ok=True)
        path = dir / file_name
        if webdriver.save_screenshot(dir / file_name):
            return path
        else:
            return None

    @property
    def webdrivers(self) -> List[WebDriver]:
        return list(self._session_driver_map.values())

    def get_request_name(self, webdriver: WebDriver):
        #if isinstance(webdriver, EventFiringWebDriver):
        #    webdriver = webdriver.wrapped_driver
        return webdriver.capabilities.get("paf:requestName")

    def __set_request_name(self, webdriver: WebDriver, request: WebDriverRequest):
        webdriver.capabilities.setdefault("paf:requestName", request.name)

def inject_config(binder: inject.Binder):
    binder.bind(WebDriverManager, WebDriverManager())
