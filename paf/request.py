import re
from urllib.parse import urlparse, ParseResult

from is_empty import empty
from selenium.webdriver.common.options import BaseOptions

from paf.common import Size, Property


class WebDriverRequest:
    def __init__(self, session: str = "default"):
        self._session = session
        self._window_size: Size = None
        self._browser: str = None
        self._browser_version: str = None
        self._options: BaseOptions = None
        self._server_url: ParseResult = None
        server_url = Property.env(Property.PAF_SELENIUM_SERVER_URL)
        if server_url:
            self.server_url = server_url

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options: BaseOptions):
        self._options = options

    @property
    def server_url(self) -> ParseResult:
        return self._server_url

    @server_url.setter
    def server_url(self, url: str | ParseResult):
        if not isinstance(url, ParseResult):
            url = urlparse(url)

        self._server_url = url

    @property
    def session(self):
        #       if empty(self._session):
        #           self._session = uuid.uuid4()
        return self._session

    def __detect_browser(self):
        match = re.search("(\w+)(?:\:(\w+))?", Property.env(Property.PAF_BROWSER_SETTING))
        if match:
            groups = match.groups()
            self._browser = groups[0]
            if not empty(groups[1]):
                self._browser_version = groups[1]

    @property
    def browser(self):
        if not self._browser:
            self.__detect_browser()
        return self._browser

    @browser.setter
    def browser(self, browser: str):
        self._browser = browser

    @property
    def browser_version(self):
        if not self._browser_version:
            self.__detect_browser()
        return self._browser_version

    @browser_version.setter
    def browser_version(self, version: str):
        self._browser_version = version

    @property
    def window_size(self):
        if not self._window_size:
            match = re.search("(\d+)x(\d+)", Property.env(Property.PAF_WINDOW_SIZE))
            groups = match.groups()
            self._window_size = Size(int(groups[0]), int(groups[1]))

        return self._window_size

    @window_size.setter
    def window_size(self, size: Size):
        self._window_size = size
