import math
from abc import abstractmethod, ABC
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Type, TypeVar, List, Generic, Iterable, Iterator, Callable, ContextManager

import inject
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.color import Color

import paf.javascript as script
from paf.assertion import StringAssertion, Format, BinaryAssertion, QuantityAssertion, RectAssertion, ASSERTION
from paf.common import HasParent, Locator, Point, Rect, Property, Formatter, NotFoundException, NotUniqueException, \
    WebdriverRetainer
from paf.control import retry
from paf.dom import Attribute
from paf.listener import Listener
from paf.locator import By
from paf.types import Mapper, R, Consumer
from paf.xpath import XPath


class UiElementActions(ABC):

    @abstractmethod
    def click(self):  # pragma: no cover
        pass

    @abstractmethod
    def hover(self):  # pragma: no cover
        pass

    @abstractmethod
    def context_click(self):  # pragma: no cover
        pass

    @abstractmethod
    def long_click(self):  # pragma: no cover
        pass

    @abstractmethod
    def double_click(self):  # pragma: no cover
        pass

    @abstractmethod
    def drag_and_drop_to(self, target_ui_element: "UiElement"):  # pragma: no cover
        pass

    @abstractmethod
    def send_keys(self, value: str):  # pragma: no cover
        pass

    @abstractmethod
    def type(self, value: str):  # pragma: no cover
        pass

    @abstractmethod
    def clear(self):  # pragma: no cover
        pass

    @abstractmethod
    def submit(self):  # pragma: no cover
        pass


T = TypeVar('T')


class PageObjectList(Generic[T], Iterable):
    @abstractmethod
    def __getitem__(self, index: int) -> T:  # pragma: no cover
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[T]:  # pragma: no cover
        pass

    @property
    def first(self) -> T:
        return self.__getitem__(0)

    @property
    def last(self) -> T:
        return self.__getitem__(-1)


class PageObject(Generic[T]):

    @abstractmethod
    def scroll_into_view(self, x: int = 0, y: int = 0):  # pragma: no cover
        pass

    @abstractmethod
    def scroll_to_top(self, x: int = 0, y: int = 0):  # pragma: no cover
        pass

    @abstractmethod
    def highlight(self, color: Color = Color.from_string("#0f0"), seconds: float = 2):  # pragma: no cover
        pass

    @abstractmethod
    def take_screenshot(self) -> Path | None:  # pragma: no cover
        pass


class UiElementTests:
    @property
    @abstractmethod
    def expect(self) -> "UiElementAssertion":  # pragma: no cover
        pass

    @property
    @abstractmethod
    def wait_for(self) -> "UiElementAssertion":  # pragma: no cover
        pass


class UiElement(
    WebdriverRetainer,
    PageObject["UiElement"],
    UiElementTests,
    UiElementActions,
    HasParent,
    PageObjectList["UiElement"],
    ABC
):
    def __str__(self):
        return self.name

    @property
    def name(self):
        if self._name:
            return self._name
        else:
            return f"UiElement({self._by.__str__()})[{self._index}]"

    @abstractmethod
    def find(self, by: Locator, name: str = None) -> "UiElement":  # pragma: no cover
        pass

    @property
    def expect(self):
        return UiElementAssertion(self)

    @property
    def wait_for(self):
        return UiElementAssertion(self, raise_exception=False)

    @abstractmethod
    def _find_web_elements(self) -> ContextManager[List[WebElement]]:
        pass

    @contextmanager
    def find_web_element(self) -> ContextManager[WebElement]:
        with self._find_web_elements() as web_elements:
            count = len(web_elements)
            if self._by.is_unique and count != 1:
                raise NotUniqueException()
            elif count > self._index:
                yield web_elements[self._index]
            else:
                raise NotFoundException()

    def _count_elements(self):
        with self._find_web_elements() as web_elements:
            return len(web_elements)


class TestableUiElement(PageObject["TestableUiElement"], UiElementTests, ABC):
    pass


class InteractiveUiElement(PageObject["InteractiveUiElement"], UiElementTests, UiElementActions, ABC):
    pass


class InexistentUiElement(UiElement):

    def __init__(self, name: str = None, parent: object = None):
        self._name = name
        self._parent = parent
        self._by = By.id(None)
        self._index = 0

    @property
    def webdriver(self):
        return None

    def scroll_into_view(self, x: int = 0, y: int = 0):
        pass

    def scroll_to_top(self, x: int = 0, y: int = 0):
        pass

    def highlight(self, color: Color = Color.from_string("#0f0"), seconds: float = 2):
        pass

    def take_screenshot(self) -> Path | None:
        pass

    def click(self):
        pass

    def hover(self):
        pass

    def context_click(self):
        pass

    def long_click(self):
        pass

    def double_click(self):
        pass

    def drag_and_drop_to(self, target_ui_element: UiElement):
        pass

    def send_keys(self, value: str):
        pass

    def type(self, value: str):
        pass

    def clear(self):
        pass

    def submit(self):
        pass

    def __getitem__(self, index: int) -> T:
        return self

    def __iter__(self) -> Iterator[T]:
        pass

    def find(self, by: Locator, name: str = None):
        return InexistentUiElement(name, self)

    @contextmanager
    def _find_web_elements(self) -> ContextManager[List[WebElement]]:
        yield []


class DefaultUiElement(UiElement):

    def __init__(
            self,
            by: Locator,
            ui_element: UiElement = None,
            webdriver: WebDriver = None,
            parent: object = None,
            index: int = 0,
            name: str = None,
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
        self._name = name

    @property
    def webdriver(self):
        return self._webdriver

    def find(self, by: Locator, name: str = None):
        return DefaultUiElement(
            by=by,
            ui_element=self,
            webdriver=self._webdriver,
            parent=self,
            name=name,
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

    @contextmanager
    def _find_web_elements(self) -> ContextManager[List[WebElement]]:
        if self._ui_element:
            with self._ui_element.find_web_element() as web_element:
                is_frame = web_element.tag_name.lower() in ("frame", "iframe")
                if is_frame:
                    self._webdriver.switch_to.frame(web_element)
                    web_elements = self._webdriver.find_elements(self._by.by, self._by.value)
                else:
                    web_elements = web_element.find_elements(self._by.by, self.__relative_selector(self._by))
                yield self._filter_web_elements(web_elements)

        elif self._webdriver:
            self._webdriver.switch_to.default_content()
            web_elements = self._webdriver.find_elements(self._by.by, self._by.value)
            yield self._filter_web_elements(web_elements)
        else:
            raise Exception(f"{self.name_path} initialized without WebDriver nor UiElement")

    # @contextmanager
    # def find_web_element(self) -> ContextManager[WebElement]:
    #     pass
    #     with self._find_web_elements() as web_elements:
    #         count = len(web_elements)
    #         if self._by.is_unique and count != 1:
    #             raise NotUniqueException()
    #         elif count > self._index:
    #             yield web_elements[self._index]
    #         else:
    #             raise NotFoundException()

    def _web_element_action_sequence(self, action: Consumer[WebElement], action_name: str):
        listener = inject.instance(Listener)

        def _sequence():
            with self.find_web_element() as web_element:
                action(web_element)

        try:
            retry(_sequence, lambda e: listener.action_failed(action_name, self, e))
            listener.action_passed(action_name, self)
        except Exception as exception:
            listener.action_failed_finally(action_name, self, exception)
            raise Exception(f"{self.name_path}: {exception}")

    def click(self):
        self._web_element_action_sequence(lambda x: x.click(), "click")
        return self

    def send_keys(self, value: str):
        self._web_element_action_sequence(lambda x: x.send_keys(value), "send_keys")
        return self

    def take_screenshot(self) -> Path | None:
        with self.find_web_element() as web_element:
            dir = Path(Property.env(Property.PAF_SCREENSHOTS_DIR))
            formatter = inject.instance(Formatter)
            file_name = f"{self.name}-{formatter.datetime(datetime.now())}.png"
            dir.mkdir(parents=True, exist_ok=True)
            path = dir / file_name
            if web_element.screenshot(str(path)):
                return path
            else:
                return None

    def type(self, value: str):
        def _action(web_element: WebElement):
            web_element.clear()
            web_element.send_keys(value)
            assert web_element.get_attribute("value") == value

        self._web_element_action_sequence(_action, "type")
        return self

    def hover(self):
        def _action(web_element: WebElement):
            actions = ActionChains(self._webdriver)
            actions.move_to_element(web_element).perform()

        self._web_element_action_sequence(_action, "hover")

    def context_click(self):
        def _action(web_element: WebElement):
            actions = ActionChains(self._webdriver)
            actions.context_click(web_element).perform()

        self._web_element_action_sequence(_action, "context_click")

    def long_click(self):
        def _action(web_element: WebElement):
            actions = ActionChains(self._webdriver)
            actions.click_and_hold(web_element).perform()

        self._web_element_action_sequence(_action, "long_click")

    def double_click(self):
        def _action(web_element: WebElement):
            actions = ActionChains(self._webdriver)
            actions.double_click(web_element).perform()

        self._web_element_action_sequence(_action, "double_click")

    def drag_and_drop_to(self, target_ui_element: "UiElement"):
        def _action(web_element: WebElement):
            with target_ui_element.find_web_element() as target:
                actions = ActionChains(self._webdriver)
                actions.drag_and_drop(web_element, target).perform()

        self._web_element_action_sequence(_action, "drag_and_drop_to")

    def clear(self):
        self._web_element_action_sequence(lambda x: x.clear(), "clear")
        return self

    def submit(self):
        self._web_element_action_sequence(lambda x: x.submit(), "submit")
        return self

    def scroll_into_view(self, x: int = 0, y: int = 0):
        def _action(web_element: WebElement):
            script.scroll_to_center(self._webdriver, web_element, Point(x, y))

        self._web_element_action_sequence(_action, "scroll_into_view")

    def scroll_to_top(self, x: int = 0, y: int = 0):
        def _action(web_element: WebElement):
            script.scroll_to_top(self._webdriver, web_element, Point(x, y))

        self._web_element_action_sequence(_action, "scroll_to_top")

    def highlight(self, color: Color = Color.from_string("#0f0"), seconds: float = 2):
        def _action(web_element: WebElement):
            script.highlight(self._webdriver, web_element, color, math.floor(seconds * 1000))

        self._web_element_action_sequence(_action, "highlight")

    def __iter__(self):
        for i in range(self._count_elements()):
            yield self.__getitem__(i)

    def __getitem__(self, index: int):
        return DefaultUiElement(
            ui_element=self._ui_element,
            webdriver=self._webdriver,
            by=self._by,
            parent=self._parent,
            index=index
        )


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
            assertion_class: Type[ASSERTION],
            mapper: Mapper[WebElement, any],
            property_name: str
    ) -> ASSERTION:

        def _map_failsafe():
            try:
                with self._ui_element.find_web_element() as web_element:
                    return mapper(web_element)
            except Exception:
                return None

        def _map():
            with self._ui_element.find_web_element() as web_element:
                return mapper(web_element)

        return assertion_class(
            parent=self._ui_element,
            actual_supplier=_map,
            name_supplier=lambda: f".{property_name} {Format.param(_map_failsafe())} ",
            raise_exception=self._raise,
        )

    @property
    def text(self):
        return self._map_web_element_property(StringAssertion, lambda x: x.text, "text")

    def displayed(self, expected: bool):
        return self._map_web_element_property(BinaryAssertion, lambda x: x.is_displayed(), "displayed").be(expected)

    def enabled(self, expected: bool):
        return self._map_web_element_property(BinaryAssertion, lambda x: x.is_enabled(), "enabled").be(expected)

    def selected(self, expected: bool):
        return self._map_web_element_property(BinaryAssertion, lambda x: x.is_selected(), "selected").be(expected)

    @property
    def tag_name(self):
        return self._map_web_element_property(StringAssertion, lambda x: x.tag_name, "tag name")

    def attribute(self, attribute: str | Attribute):
        if isinstance(attribute, Attribute):
            attribute = attribute.value

        return self._map_web_element_property(StringAssertion, lambda x: x.get_attribute(attribute),
                                              f"attribute({attribute})")

    def css(self, property_name: str):
        return self._map_web_element_property(StringAssertion, lambda x: x.value_of_css_property(property_name),
                                              f"css({property_name}")

    def classes(self, *classes):
        return self.attribute(Attribute.CLASS).has_words(*classes)

    def visible(self, expected: bool):
        return self._visible(expected, False)

    def fully_visible(self, expected: bool):
        return self._visible(expected, True)

    def _visible(self, expected: bool, fully: bool = False):
        def _map(web_element: WebElement):
            viewport = script.get_viewport(self._ui_element.webdriver)
            bounds = Rect.from_web_element(web_element)
            if fully:
                return viewport.contains(bounds)
            else:
                return viewport.intersects(bounds)

        name = "visible"
        if fully:
            name = f"fully {name}"

        return self._map_web_element_property(BinaryAssertion, _map, name).be(expected)

    @property
    def value(self):
        return self.attribute("value")

    @property
    def count(self):
        def failsafe_count_elements():
            try:
                return self._ui_element._count_elements()
            except:
                return 0

        return QuantityAssertion[int](
            parent=self._ui_element,
            actual_supplier=failsafe_count_elements,
            name_supplier=lambda: f" count {Format.param(failsafe_count_elements())} ",
            raise_exception=self._raise,
        )

    @property
    def bounds(self):
        return self._map_web_element_property(RectAssertion, lambda x: Rect.from_web_element(x), "bounds")
