from typing import TypeVar, List, Generic

from core.by import By
from core.page import HasParent
from core.uielement import UiElement, UiElementActions, PageObject, TestableUiElement
from core.xpath import XPath

T = TypeVar("T")


class Component(Generic[T], HasParent, UiElementActions, PageObject, TestableUiElement):

    def __init__(self, ui_element: UiElement):
        self._ui_element = ui_element
        ui_element._parent = self

    def click(self):
        self._ui_element.click()
        return self

    def send_keys(self, value: str):
        self._ui_element.send_keys(value)
        return self

    def input(self, value: str):
        self._ui_element.input(value)
        return self

    def clear(self):
        self._ui_element.clear()
        return self

    def find(self, by: By | XPath):
        return self._ui_element.find(by)

    @property
    def name(self):
        return f"{self.__class__.__name__}"

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


class ComponentList(Generic[T]):

    def __init__(
        self,
        component: Component,
        parent: HasParent = None
    ):
        self._component = component
        self._parent = parent

    def __getitem__(self, index: int) -> T:
        return UiElement(
            ui_element=self._ui_element._ui_element,
            webdriver=self._ui_element._webdriver,
            by=self._ui_element._by,
            parent=self._parent,
            index=index
        )

    @property
    def first(self):
        return self.__getitem__(0)

    @property
    def last(self):
        return self.__getitem__(-1)
