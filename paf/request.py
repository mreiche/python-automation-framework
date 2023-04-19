import os
import re

from is_empty import empty

from paf.common import Size


# import uuid
# from is_empty import empty


class WebDriverRequest:
    def __init__(self):
        self._session = "default"
        self._window_size: Size = None
        self._browser: str = None
        self._browser_version: str = None

    @property
    def session(self):
        #       if empty(self._session):
        #           self._session = uuid.uuid4()
        return self._session

    @session.setter
    def session(self, session: str):
        self._session = session

    def __detect_browser(self):
        match = re.search("(\w+)(?:\:(\w+))?", os.getenv("PAF_BROWSER_SETTING", "chrome"))
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

    @property
    def browser_version(self):
        if not self._browser_version:
            self.__detect_browser()
        return self._browser_version

    @property
    def window_size(self):
        if not self._window_size:
            match = re.search("(\d+)x(\d+)", os.getenv("PAF_WINDOW_SIZE", "1920x1080"))
            groups = match.groups()
            self._window_size = Size(int(groups[0]), int(groups[1]))

        return self._window_size
