from typing import TypeVar, Generic, Type

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
        return self._ui_element.find(by)

    @property
    def name(self):
        return f"{self.__class__.__name__}"

    def __str__(self):
        return self.name

    @property
    def list(self):
        return ComponentList[T](self.__class__, self._ui_element)

    @property
    def expect(self):
        return self._ui_element.expect

    @property
    def wait_for(self):
        return self._ui_element.wait_for


#C = TypeVar("C")

# class ComponentCreator:
#     def _create_component(self, component_class: Type[C], ui_element: UiElement) -> C:
#         pass


class ComponentList(PageObjectList[T]):

    def __init__(
        self,
        component_class: Type[T],
        ui_element: UiElement
    ):
        self._ui_element = ui_element
        self._component_class = component_class

    def __iter__(self):
        i = 0
        for _ in self._ui_element._find_web_elements():
            yield self.__getitem__(i)
            i += 1

    def __getitem__(self, index: int) -> T:
        ui_element = UiElement(
            ui_element=self._ui_element._ui_element,
            webdriver=self._ui_element._webdriver,
            by=self._ui_element._by,
            parent=self._ui_element._parent,
            index=index
        )
        return self._component_class(ui_element)
