from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.options import BaseOptions

from paf.types import Consumer
from paf.request import WebDriverRequest
from selenium.webdriver import Chrome, Firefox, Edge, Safari
from selenium.webdriver.remote.webdriver import WebDriver
from is_empty import empty
import inject


class WebDriverManager:
    def __init__(self):
        self._driver_map: dict[str, WebDriver] = {}
        self._user_agent_config: dict[str, Consumer[BaseOptions]] = {}

    def _configure_options(self, request: WebDriverRequest, options: BaseOptions):
        if request.browser in self._user_agent_config:
            self._user_agent_config[request.browser](options)
        return options

    def get_webdriver(self, request: WebDriverRequest = None) -> WebDriver:
        if not request:
            request = WebDriverRequest()

        session_key = request.session
        if session_key in self._driver_map:
            return self._driver_map[session_key]

        webdriver = None

        if empty(request.browser) or request.browser in ["chrome", "chromium"]:
            options = self._configure_options(request, ChromeOptions())
            webdriver = Chrome(chrome_options=options)
        elif request.browser in ["firefox"]:
            options = self._configure_options(request, FirefoxOptions())
            webdriver = Firefox(options=options)
        elif request.browser in ["edge"]:
            webdriver = Edge()
        elif request.browser in ["safari"]:
            webdriver = Safari()

        if not webdriver:
            raise Exception("No browser specified")

        self._driver_map[session_key] = webdriver

        return webdriver

    def shutdown_session(self, session_key):
        pass

    def shutdown(self, webdriver: WebDriver):
        webdriver.quit()
        webdrivers = list(self._driver_map.values())
        index = webdrivers.index(webdriver)

        session_keys = list(self._driver_map.keys())
        key = session_keys[index]
        self._driver_map.pop(key)

    def shutdown_all(self):
        for webdriver in list(self._driver_map.values()):
            self.shutdown(webdriver)


def inject_config(binder: inject.Binder):
    binder.bind(WebDriverManager, WebDriverManager())
