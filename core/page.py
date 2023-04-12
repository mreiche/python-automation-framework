from selenium.webdriver.remote.webdriver import WebDriver

from core.assertion import StringAssertion, Format
from core.by import By
from core.config import TestConfig


class Page:
    def __init__(self, webdriver: WebDriver):
        self._webdriver = webdriver

    def find(self, by: By) -> "UiElement":
        from core.uielement import UiElement
        return UiElement(self._webdriver, by, self)

    def open(self, url: str):
        self._webdriver.get(url)
        return self

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def expect(self):
        return PageAssertion(self, self._webdriver)

    @property
    def wait_for(self):
        return PageAssertion(self, self._webdriver, TestConfig(raise_exception=False))


class PageAssertion:

    def __init__(
        self,
        page: Page,
        webdriver: WebDriver,
        config: TestConfig = TestConfig(),
    ):
        self._page = page
        self._webdriver = webdriver
        self._raise = config.raise_exception

    @property
    def title(self):
        return StringAssertion(
            parent=None,
            actual=lambda: self._webdriver.title,
            subject=lambda: f"{self._page.name}.title {Format.param(self._webdriver.title)}",
            raise_exceptions=self._raise,
        )

    @property
    def url(self):
        return StringAssertion(
            parent=None,
            actual=lambda: self._webdriver.current_url,
            subject=lambda: f"{self._page.name}.url {Format.param(self._webdriver.current_url)}",
            raise_exceptions=self._raise,
        )
