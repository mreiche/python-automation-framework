from typing import TypeVar

from selenium.webdriver.support.color import Color

from paf.common import HasParent, Locator, Point
from paf.uielement import UiElement, PageObject, PageObjectList

T = TypeVar("T")


class Component(PageObject[T], PageObjectList[T], HasParent):

    def highlight(self, color: Color = Color.from_string("#0f0"), seconds: float = 2):
        self._ui_element.highlight(color, seconds)
        return self

    def __init__(self, ui_element: UiElement):
        self._ui_element = ui_element
        ui_element._parent = self

    def _find(self, by: Locator):
        ui_element = self._ui_element.find(by)
        ui_element._parent = self
        return ui_element

    @property
    def name(self):
        return f"{self.__class__.__name__}({self._ui_element.name})"

    def __str__(self):
        return self.name

    def scroll_into_view(self, offset: Point = Point()):
        self._ui_element.scroll_into_view(offset)

    def scroll_to_top(self, offset: Point = Point()):
        self._ui_element.scroll_to_top(offset)

    def __iter__(self):
        for i in range(self._ui_element._count_elements()):
            yield self.__getitem__(i)

    def __getitem__(self, index: int) -> T:
        ui_element = UiElement(
            ui_element=self._ui_element._ui_element,
            webdriver=self._ui_element._webdriver,
            by=self._ui_element._by,
            index=index
        )
        component = self.__class__(ui_element)
        component._parent = self._parent
        return component
