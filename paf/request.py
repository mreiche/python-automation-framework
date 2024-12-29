import os
import re
from urllib.parse import urlparse, ParseResult

from is_empty import empty
from selenium.webdriver.common.options import BaseOptions

from paf.common import Size, Property, Point, Rect


def _read_coordinates(input_string: str) -> tuple[int, int]:
    match = re.search("(\\d+)x(\\d+)", input_string)
    groups = match.groups()
    return int(groups[0]), int(groups[1])


def _is_true(input_string: str) -> bool:
    normalized = input_string.strip().lower()
    return normalized in ("1", "true", "on")


class WebDriverRequest:
    def __init__(self, session_name: str = "default"):
        self._session_name = session_name
        self._window_size: Size = None
        self._window_position: Point = None
        self._window_maximize = None
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
    def session_name(self):
        return self._session_name

    def __detect_browser(self):
        match = re.search("(\\w+)(?::(\\w+))?", Property.env(Property.PAF_BROWSER_SETTING))
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
    def window_size(self) -> Size | None:
        if not self._window_size and Property.PAF_WINDOW_SIZE.name in os.environ:
            coords = _read_coordinates(Property.env(Property.PAF_WINDOW_SIZE))
            self.window_size = Size(coords[0], coords[1])

        return self._window_size

    @window_size.setter
    def window_size(self, size: Size):
        self._window_size = size

    @property
    def window_position(self) -> Point | None:
        if not self._window_position and Property.PAF_WINDOW_POSITION.name in os.environ:
            coords = _read_coordinates(Property.env(Property.PAF_WINDOW_POSITION))
            self.window_position = Point(coords[0], coords[1])

        return self._window_position

    @window_position.setter
    def window_position(self, point: Point):
        self._window_position = point

    @property
    def window_maximize(self) -> bool | None:
        if self._window_maximize is None and Property.PAF_WINDOW_MAXIMIZE.name in os.environ:
            self.window_maximize = _is_true(Property.env(Property.PAF_WINDOW_MAXIMIZE))

        return self._window_maximize

    @window_maximize.setter
    def window_maximize(self, maximize: bool):
        self._window_maximize = maximize

    def __str__(self):
        dict = self.__dict__
        if self._options:
            dict["_options"] = self._options.__dict__
        return dict.__str__()
