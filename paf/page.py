from typing import Type, TypeVar

import inject
from selenium.webdriver.remote.webdriver import WebDriver

from paf.assertion import StringAssertion, Format
from paf.common import HasName, Locator
from paf.manager import WebDriverManager

C = TypeVar("C")
P = TypeVar("P")


class PageFactory:
    def create_page(self, page_class: Type[P], webdriver: WebDriver = None) -> P:
        if not webdriver:
            webdriver = inject.instance(WebDriverManager).get_webdriver()

        return page_class(webdriver)


class BasePage(HasName):
    def __init__(self, webdriver: WebDriver):
        self._webdriver = webdriver

    def open(self, url: str):
        self._webdriver.get(url)
        return self

    @property
    def webdriver(self):
        return self._webdriver

    def __str__(self):
        return self.name

    def _find(self, by: Locator):
        from paf.uielement import UiElement
        return UiElement(by, webdriver=self._webdriver, parent=self)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def expect(self):
        return PageAssertion(self, self._webdriver)

    @property
    def wait_for(self):
        return PageAssertion(self, self._webdriver, raise_exception=False)


class FinderPage(BasePage):
    def find(self, by: Locator):
        ui_element = self._find(by)
        ui_element._parent = None
        return ui_element


class Page(BasePage):
    def __init__(self, webdriver: WebDriver):
        super().__init__(webdriver)

    def _create_component(self, component_class: Type[C], ui_element: "UiElement") -> C:
        component = component_class(ui_element)
        component._parent = self
        return component

    def _create_page(self, page_class: Type[P]) -> P:
        return page_class(self._webdriver)


class PageAssertion:

    def __init__(
        self,
        page: BasePage,
        webdriver: WebDriver,
        raise_exception: bool = True
    ):
        self._page = page
        self._webdriver = webdriver
        self._raise = raise_exception

    @property
    def title(self):
        return StringAssertion(
            parent=None,
            actual=lambda: self._webdriver.title,
            subject=lambda: f"{self._page.name}.title {Format.param(self._webdriver.title)}",
            raise_exception=self._raise,
        )

    @property
    def url(self):
        return StringAssertion(
            parent=None,
            actual=lambda: self._webdriver.current_url,
            subject=lambda: f"{self._page.name}.url {Format.param(self._webdriver.current_url)}",
            raise_exception=self._raise,
        )


def inject_config(binder: inject.Binder):
    binder.bind(PageFactory, PageFactory())
