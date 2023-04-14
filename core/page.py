from typing import Type, TypeVar

from selenium.webdriver.remote.webdriver import WebDriver

from core.assertion import StringAssertion, Format
from core.by import By
from core.config import TestConfig
from core.xpath import XPath
from abc import ABC, abstractmethod


class HasName(ABC):
    @property
    @abstractmethod
    def name(self):
        pass


class HasParent(HasName, ABC):
    @property
    def _parent(self):
        return self.__parent

    @_parent.setter
    def _parent(self, parent: "HasParent"):
        self.__parent = parent

    @property
    def name_path(self):
        path = [self]
        inst = self
        while hasattr(inst, "_parent") and inst._parent:
            path.append(inst._parent)
            inst = inst._parent

        return " > ".join(map(str, reversed(path)))


C = TypeVar("C")
P = TypeVar("P")


class Page(HasName):
    def __init__(self, webdriver: WebDriver):
        self._webdriver = webdriver
        self.init()

    def find(self, by: By | XPath) -> "UiElement":
        from core.uielement import UiElement
        if isinstance(by, XPath):
            by = By.xpath(str(by))

        return UiElement(by, webdriver=self._webdriver, parent=self)

    def init(self):
        pass

    def create_component(self, component_class: Type[C], ui_element: "UiElement") -> C:
        component = component_class(ui_element)
        component._parent = self
        return component

    def create_page(self, page_class: Type[P]) -> P:
        return page_class(self._webdriver)

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
        self._config = config

    @property
    def title(self):
        return StringAssertion(
            parent=None,
            actual=lambda: self._webdriver.title,
            subject=lambda: f"{self._page.name}.title {Format.param(self._webdriver.title)}",
            config=self._config,
        )

    @property
    def url(self):
        return StringAssertion(
            parent=None,
            actual=lambda: self._webdriver.current_url,
            subject=lambda: f"{self._page.name}.url {Format.param(self._webdriver.current_url)}",
            config=self._config,
        )
