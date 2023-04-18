from typing import TypeVar, Generic, List

from selenium.webdriver.remote.webelement import WebElement

from paf.common import HasParent, Locator
from paf.uielement import UiElement, UiElementActions, PageObject, TestableUiElement, PageObjectList

T = TypeVar("T")


class Component(Generic[T], HasParent, UiElementActions, TestableUiElement, PageObject[T]):

    def __init__(self, ui_element: UiElement):
        self._ui_element = ui_element
        ui_element._parent = self

    def click(self):
        self._ui_element.click()
        return self

    def send_keys(self, value: str):
        self._ui_element.send_keys(value)
        return self

    def type(self, value: str):
        self._ui_element.type(value)
        return self

    def clear(self):
        self._ui_element.clear()
        return self

    def _find(self, by: Locator):
        ui_element = self._ui_element.find(by)
        ui_element._parent = self
        return ui_element

    @property
    def name(self):
        return f"{self.__class__.__name__}({self._ui_element.name})"

    def __str__(self):
        return self.name

    @property
    def list(self):
        return ComponentList[T](self)

    @property
    def expect(self):
        return self._ui_element.expect

    @property
    def wait_for(self):
        return self._ui_element.wait_for


class ComponentList(PageObjectList[T]):

    def __init__(self, component: Component[T]):
        self._component = component

    def __iter__(self):
        count = 0

        def _count(web_elements: List[WebElement]):
            nonlocal count
            count = len(web_elements)

        self._component._ui_element._find_web_elements(_count)

        for i in range(count):
            yield self.__getitem__(i)

    def __getitem__(self, index: int) -> T:
        ui_element = UiElement(
            ui_element=self._component._ui_element._ui_element,
            webdriver=self._component._ui_element._webdriver,
            by=self._component._ui_element._by,
            index=index
        )
        component = self._component.__class__(ui_element)
        component._parent = self._component._parent
        return component
