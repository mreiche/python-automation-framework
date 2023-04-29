from typing import Type

from selenium.webdriver.support.color import Color

from paf.common import HasParent, Locator, Point
from paf.types import COMPONENT, PAGE
from paf.uielement import UiElement, PageObject, PageObjectList, UiElementTests


class Component(PageObject[COMPONENT], PageObjectList[COMPONENT], HasParent, UiElementTests):

    def highlight(self, color: Color = Color.from_string("#0f0"), seconds: float = 2):
        self._ui_element.highlight(color, seconds)
        return self

    def __init__(self, ui_element: UiElement):
        self._ui_element = ui_element
        ui_element._parent = self

    def _find(self, by: Locator):
        ui_element = self._ui_element.find(by)
        #ui_element._parent = self
        return ui_element

    @property
    def name(self):
        return f"{self.__class__.__name__}"

    @property
    def name_path(self):
        return self._ui_element.name_path

    def __str__(self):
        return self.name

    def scroll_into_view(self, offset: Point = Point()):
        self._ui_element.scroll_into_view(offset)

    def scroll_to_top(self, offset: Point = Point()):
        self._ui_element.scroll_to_top(offset)

    def __iter__(self):
        for i in range(self._ui_element._count_elements()):
            yield self.__getitem__(i)

    def __getitem__(self, index: int) -> COMPONENT:
        ui_element = UiElement(
            ui_element=self._ui_element._ui_element,
            webdriver=self._ui_element._webdriver,
            by=self._ui_element._by,
            index=index
        )
        component = self.__class__(ui_element)
        component._parent = self._parent
        return component

    def _create_component(self, component_class: Type[COMPONENT], ui_element: "UiElement") -> COMPONENT:
        component = component_class(ui_element)
        component._parent = self
        return component

    def _create_page(self, page_class: Type[PAGE]) -> PAGE:
        return page_class(self._ui_element.webdriver)

    @property
    def expect(self):
        return self._ui_element.expect

    @property
    def wait_for(self):
        return self._ui_element.wait_for
