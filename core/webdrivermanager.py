from core.webdriverrequest import WebDriverRequest
from selenium.webdriver import Chrome, Firefox, Edge, Safari
from selenium.webdriver.remote.webdriver import WebDriver
from is_empty import empty

class WebDriverManager:

    _driver_map: dict[str, WebDriver] = {}

    def get_webdriver(self, request: WebDriverRequest = None) -> WebDriver:
        if not request:
            request = WebDriverRequest()

        session_key = request.session
        if session_key in self._driver_map:
            return self._driver_map[session_key]

        webdriver = None

        if empty(request.browser) or request.browser in ["chrome", "chromium"]:
            webdriver = Chrome()
        elif request.browser in ["firefox"]:
            webdriver = Firefox()
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
