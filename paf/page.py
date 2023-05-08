from typing import Type

import inject
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver

from paf.assertion import StringAssertion, Format
from paf.common import HasName, Locator
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest
from paf.types import PAGE, COMPONENT


class PageFactory:
    def create_page(self, page_class: Type[PAGE], webdriver: WebDriver = None) -> PAGE:
        if not webdriver:
            webdriver = inject.instance(WebDriverManager).get_webdriver(WebDriverRequest())

        return page_class(webdriver)


class BasePage(HasName):
    def __init__(self, webdriver: WebDriver):
        self._webdriver = webdriver

    def open(self, url: str):
        self._webdriver.get(url)
        return self

    def __str__(self):
        return self.name

    def _find(self, by: Locator):
        from paf.uielement import UiElement
        return UiElement(by, webdriver=self._webdriver, parent=self)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def webdriver(self):
        return self._webdriver

    @property
    def expect(self):
        return PageAssertion(self, self._webdriver)

    @property
    def wait_for(self):
        return PageAssertion(self, self._webdriver, raise_exception=False)

    def scroll_by(self, x: int = 0, y: int = 0):
        actions = ActionChains(self._webdriver)
        actions.scroll_by_amount(x, y).perform()


class FinderPage(BasePage):
    def find(self, by: Locator):
        ui_element = self._find(by)
        ui_element._parent = None
        return ui_element


class Page(BasePage):
    def __init__(self, webdriver: WebDriver):
        super().__init__(webdriver)

    def _create_component(self, component_class: Type[COMPONENT], ui_element: "UiElement") -> COMPONENT:
        component = component_class(ui_element)
        component._parent = self
        return component

    def _create_page(self, page_class: Type[PAGE]) -> PAGE:
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
            parent=self._page,
            actual=lambda: self._webdriver.title,
            name=lambda: f".title {Format.param(self._webdriver.title)}",
            raise_exception=self._raise,
        )

    @property
    def url(self):
        return StringAssertion(
            parent=self._page,
            actual=lambda: self._webdriver.current_url,
            subject=lambda: f".url {Format.param(self._webdriver.current_url)}",
            raise_exception=self._raise,
        )


def inject_config(binder: inject.Binder):
    binder.bind(PageFactory, PageFactory())
