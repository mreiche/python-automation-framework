import math
import re
from abc import abstractmethod, ABC
from datetime import datetime
from pathlib import Path
from typing import Type, TypeVar, List, Generic, Iterable, Iterator

import inject
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.color import Color

import paf.javascript as script
from paf.assertion import StringAssertion, Format, BinaryAssertion, QuantityAssertion, RectAssertion
from paf.common import HasParent, Locator, Point, Rect, Property, Formatter
from paf.control import Control
from paf.dom import Attribute
from paf.locator import By
from paf.types import Mapper, Consumer, R
from paf.xpath import XPath


class UiElementActions:

    @abstractmethod
    def click(self):
        pass

    @abstractmethod
    def hover(self):
        pass

    @abstractmethod
    def context_click(self):
        pass

    @abstractmethod
    def long_click(self):
        pass

    @abstractmethod
    def double_click(self):
        pass

    @abstractmethod
    def drag_and_drop_to(self, target_ui_element: "UiElement"):
        pass

    @abstractmethod
    def send_keys(self, value: str):
        pass

    @abstractmethod
    def type(self, value: str):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def submit(self):
        pass


T = TypeVar('T')


class PageObjectList(Generic[T], Iterable):
    @abstractmethod
    def __getitem__(self, index: int) -> T:
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        pass

    @property
    def first(self) -> T:
        return self.__getitem__(0)

    @property
    def last(self) -> T:
        return self.__getitem__(-1)


class PageObject(Generic[T]):

    @abstractmethod
    def scroll_into_view(self, x: int = 0, y: int = 0):
        pass

    @abstractmethod
    def scroll_to_top(self, x: int = 0, y: int = 0):
        pass

    @abstractmethod
    def highlight(self, color: Color = Color.from_string("#0f0"), seconds: float = 2):
        pass


class UiElementTests:
    @property
    @abstractmethod
    def expect(self) -> "UiElementAssertion":
        pass

    @property
    @abstractmethod
    def wait_for(self) -> "UiElementAssertion":
        pass


class TestableUiElement(PageObject["TestableUiElement"], UiElementTests, ABC):
    pass


class InteractiveUiElement(PageObject["InteractiveUiElement"], UiElementTests, UiElementActions, ABC):
    pass


class UiElement(UiElementTests, UiElementActions, HasParent, PageObjectList["UiElement"]):

    def __init__(
        self,
        by: Locator,
        ui_element: "UiElement" = None,
        webdriver: WebDriver = None,
        parent: object = None,
        index: int = 0,
    ):

        if isinstance(by, XPath):
            by = By.xpath(str(by))
        elif isinstance(by, str):
            by = By.css_selector(by)

        self._webdriver = webdriver
        self._ui_element = ui_element
        self._by = by
        self._index = index
        self._parent = parent

    @property
    def webdriver(self):
        return self._webdriver

    def find(self, by: Locator):
        return UiElement(
            by=by,
            ui_element=self,
            webdriver=self._webdriver,
            parent=self
        )

    def __relative_selector(self, by: By):
        if by.by == SeleniumBy.XPATH and by.value.startswith("/"):
            return f".{by.value}"
        else:
            return by.value

    def _filter_web_elements(self, web_elements: List[WebElement]):
        if self._by.get_filter():
            return list(filter(self._by.get_filter(), web_elements))
        else:
            return web_elements

    def _find_web_elements(self, consumer: Mapper[List[WebElement], R]) -> R:
        if self._ui_element:
            def _handle(web_element: WebElement):

                is_frame = web_element.tag_name.lower() in ("frame", "iframe")
                if is_frame:
                    self._webdriver.switch_to.frame(web_element)
                    web_elements = self._webdriver.find_elements(self._by.by, self._by.value)
                else:
                    web_elements = web_element.find_elements(self._by.by, self.__relative_selector(self._by))

                return consumer(self._filter_web_elements(web_elements))

            return self._ui_element.find_web_element(_handle)
        elif self._webdriver:
            self._webdriver.switch_to.default_content()
            web_elements = self._webdriver.find_elements(self._by.by, self._by.value)
            return consumer(self._filter_web_elements(web_elements))
        else:
            raise Exception("UiElement initialized without WebDriver nor UiElement")

    def find_web_element(self, mapper: Mapper[WebElement, R]) -> R:
        def _handle(web_elements: List[WebElement]):
            count = len(web_elements)

            if self._by.is_unique and count != 1:
                raise Exception(f"Not unique")
            elif count > self._index:
                web_element = web_elements[self._index]
                return mapper(web_element)
            else:
                raise Exception(f"Not found")

        return self._find_web_elements(_handle)

    def _action_sequence(self, consumer: Consumer[WebElement]):
        control = inject.instance(Control)
        try:
            control.retry(lambda: self.find_web_element(consumer))
        except Exception as exception:
            raise Exception(f"{self.name_path}: {exception}")

    def click(self):
        self._action_sequence(lambda web_element: web_element.click())
        return self

    def send_keys(self, value: str):
        self._action_sequence(lambda web_element: web_element.send_keys(value))
        return self

    def take_screenshot(self) -> Path | None:
        def _handle(web_element: WebElement):
            dir = Path(Property.env(Property.PAF_SCREENSHOTS_DIR))
            formatter = inject.instance(Formatter)
            file_name = f"{self.name}-{formatter.datetime(datetime.now())}.png"
            dir.mkdir(parents=True, exist_ok=True)
            path = dir / file_name
            if web_element.screenshot(str(path)):
                return path
            else:
                return None

        return self.find_web_element(_handle)

    def type(self, value: str):
        def _action(web_element: WebElement):
            web_element.clear()
            web_element.send_keys(value)
            assert web_element.get_attribute("value") == value

        self._action_sequence(_action)
        return self

    def hover(self):
        def _action(web_element: WebElement):
            actions = ActionChains(self._webdriver)
            actions.move_to_element(web_element).perform()

        self._action_sequence(_action)

    def context_click(self):
        def _action(web_element: WebElement):
            actions = ActionChains(self._webdriver)
            actions.context_click(web_element).perform()

        self._action_sequence(_action)

    def long_click(self):
        def _action(web_element: WebElement):
            actions = ActionChains(self._webdriver)
            actions.click_and_hold(web_element).perform()

        self._action_sequence(_action)

    def double_click(self):
        def _action(web_element: WebElement):
            actions = ActionChains(self._webdriver)
            actions.double_click(web_element).perform()

        self._action_sequence(_action)

    def drag_and_drop_to(self, target_ui_element: "UiElement"):
        def _action(source: WebElement):
            def _target_found(target: WebElement):
                actions = ActionChains(self._webdriver)
                actions.drag_and_drop(source, target).perform()
            target_ui_element.find_web_element(_target_found)

        self._action_sequence(_action)

    @property
    def expect(self):
        return UiElementAssertion(self)

    @property
    def wait_for(self):
        return UiElementAssertion(self, raise_exception=False)

    def clear(self):
        self._action_sequence(lambda web_element: web_element.clear())
        return self

    def submit(self):
        self._action_sequence(lambda web_element: web_element.submit())
        return self

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f"UiElement({self._by.__str__()})[{self._index}]"

    def scroll_into_view(self, x: int = 0, y: int = 0):
        self._action_sequence(lambda web_element: script.scroll_to_center(self._webdriver, web_element, Point(x, y)))

    def scroll_to_top(self, x: int = 0, y: int = 0):
        self._action_sequence(lambda web_element: script.scroll_to_top(self._webdriver, web_element, Point(x, y)))

    def _count_elements(self):
        count = 0

        def _count(web_elements: List[WebElement]):
            nonlocal count
            count = len(web_elements)

        self._find_web_elements(_count)
        return count

    def highlight(self, color: Color = Color.from_string("#0f0"), seconds: float = 2):
        def _handle(web_element: WebElement):
            script.highlight(self._webdriver, web_element, color, math.floor(seconds * 1000))

        self.find_web_element(_handle)

    def __iter__(self):
        for i in range(self._count_elements()):
            yield self.__getitem__(i)

    def __getitem__(self, index: int):
        return UiElement(
            ui_element=self._ui_element,
            webdriver=self._webdriver,
            by=self._by,
            parent=self._parent,
            index=index
        )


A = TypeVar('A')

class UiElementAssertion:

    def __init__(
        self,
        ui_element: UiElement,
        raise_exception: bool = True,
    ):
        self._ui_element = ui_element
        self._raise = raise_exception

    def _map_web_element_property(
        self,
        assertion_class: Type[A],
        mapper: Mapper[WebElement, any],
        property_name: str
    ) -> A:
        return assertion_class(
            parent=None,
            actual=lambda: self._ui_element.find_web_element(mapper),
            subject=lambda: f"{self._ui_element.name_path}.{property_name} {Format.param(self._ui_element.find_web_element(mapper))}",
            raise_exception=self._raise,
        )

    @property
    def text(self):
        def _map(web_element: WebElement):
            return web_element.text

        return self._map_web_element_property(StringAssertion, _map, "text")

    @property
    def displayed(self):
        def _map(web_element: WebElement):
            return web_element.is_displayed()

        return self._map_web_element_property(BinaryAssertion, _map, "displayed")

    @property
    def enabled(self):
        def _map(web_element: WebElement):
            return web_element.is_enabled()

        return self._map_web_element_property(BinaryAssertion, _map, "enabled")

    @property
    def selected(self):
        def _map(web_element: WebElement):
            return web_element.is_selected()

        return self._map_web_element_property(BinaryAssertion, _map, "selected")

    @property
    def tag_name(self):
        def _map(web_element: WebElement):
            return web_element.tag_name

        return self._map_web_element_property(StringAssertion, _map, "tag name")

    def attribute(self, attribute: str|Attribute):
        if isinstance(attribute, Attribute):
            attribute = attribute.value

        def _map(web_element: WebElement):
            return web_element.get_attribute(attribute)

        return self._map_web_element_property(StringAssertion, _map, f"attribute({attribute})")

    def css(self, property_name: str):
        def _map(web_element: WebElement):
            return web_element.value_of_css_property(property_name)

        return self._map_web_element_property(StringAssertion, _map, f"css({property_name}")

    def classes(self, *classes):
        return self.attribute(Attribute.CLASS).has_words(*classes)

    @property
    def visible(self):
        return self._visible(False)

    @property
    def fully_visible(self):
        return self._visible(True)

    def _visible(self, fully: bool = False):
        def _map(web_element: WebElement):
            viewport = script.get_viewport(self._ui_element._webdriver)
            bounds = Rect.from_web_element(web_element)
            if fully:
                return viewport.contains(bounds)
            else:
                return viewport.intersects(bounds)

        name = "visible"
        if fully:
            name = f"fully {name}"

        return self._map_web_element_property(BinaryAssertion, _map, name)

    @property
    def value(self):
        return self.attribute("value")

    @property
    def count(self):
        return QuantityAssertion[int](
            parent=None,
            actual=lambda: self._ui_element._count_elements(),
            subject=lambda: f"{self._ui_element.name_path} count {Format.param(self._ui_element._count_elements())}",
            raise_exception=self._raise,
        )

    @property
    def bounds(self):
        def _map(web_element: WebElement):
            return Rect.from_web_element(web_element)

        return self._map_web_element_property(RectAssertion, _map, "bounds")
