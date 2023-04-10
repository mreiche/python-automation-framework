import os
#import uuid
#from is_empty import empty


class WebDriverRequest:
    _session = "default"

    @property
    def session(self):
 #       if empty(self._session):
 #           self._session = uuid.uuid4()
        return self._session

    @session.setter
    def session(self, session: str):
        self._session = session

    @property
    def browser(self):
        return os.getenv("TT_BROWSER_SETTING")

    @property
    def browser_version(self):
        return ""
