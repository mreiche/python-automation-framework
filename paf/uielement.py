from abc import abstractmethod, ABC
from typing import Callable, Type, TypeVar, List, Generic, Iterable, Iterator

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from paf.assertion import StringAssertion, Format, BinaryAssertion, QuantityAssertion
from paf.common import HasParent, TestConfig, Locator, Location
from paf.locator import By
from paf.retry import Sequence
from paf.types import Mapper, Consumer
from paf.xpath import XPath
from selenium.webdriver.common.by import By as SeleniumBy
import paf.javascript as script


class UiElementActions:

    @abstractmethod
    def click(self):
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
    @property
    @abstractmethod
    def list(self) -> PageObjectList[T]:
        pass

    @abstractmethod
    def scroll_into_view(self, offset: Location = Location()):
        pass

    @abstractmethod
    def scroll_to_top(self, offset: Location = Location()):
        pass


class TestableUiElement(PageObject["TestableUiElement"]):
    @property
    @abstractmethod
    def expect(self) -> "UiElementAssertion":
        pass

    @property
    @abstractmethod
    def wait_for(self) -> "UiElementAssertion":
        pass


class InteractiveUiElement(TestableUiElement, UiElementActions, PageObject["InteractiveUiElement"], ABC):
    pass


class UiElement(InteractiveUiElement, HasParent):

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

        self._webdriver = webdriver
        self._ui_element = ui_element
        self._by = by
        self._index = index
        self._parent = parent

    def find(self, by: Locator):
        return UiElement(
            by=by,
            ui_element=self,
            webdriver=self._webdriver,
            parent=self
        )

    def _relative_selector(self, by: By):
        if by.by == SeleniumBy.XPATH:
            return by.value.replace("/", "./", 1)
        else:
            return by.value

    def _find_web_elements(self, consumer: Consumer[List[WebElement]]):
        if self._ui_element:
            def _handle(web_element: WebElement):
                value = self._relative_selector(self._by)
                web_elements = web_element.find_elements(self._by.by, value)
                consumer(web_elements)

            self._ui_element._find_web_element(_handle)
        elif self._webdriver:
            # Switch to default content
            web_elements = self._webdriver.find_elements(self._by.by, self._by.value)
            consumer(web_elements)
        else:
            raise Exception("UiElement initialized without WebDriver nor UiElement")

    def _find_web_element(self, consumer: Consumer[WebElement]):
        def _handle(web_elements: List[WebElement]):
            if self._by.get_filter():
                web_elements = list(filter(self._by.get_filter(), web_elements))

            count = len(web_elements)

            if self._by.is_unique and count != 1:
                raise Exception(f"{self.name_path}: not unique")
            elif count > self._index:
                # Switch to frame
                consumer(web_elements[self._index])
                # Switch to default content
            else:
                raise Exception(f"{self.name_path}: not found")

        self._find_web_elements(_handle)

    def _action_sequence(self, consumer: Consumer[WebElement]):
        sequence = Sequence()

        exception = None
        passed = False

        def perform_action():
            nonlocal exception
            nonlocal passed

            try:
                self._find_web_element(consumer)
                passed = True
            except Exception as e:
                exception = e
                passed = False

            return passed

        sequence.run(perform_action)

        if not passed:
            raise Exception(f"{exception} after {sequence.count} retries ({round(sequence.duration, 2)} seconds)")

    def click(self):
        self._action_sequence(lambda web_element: web_element.click())
        return self

    def send_keys(self, value: str):
        self._action_sequence(lambda web_element: web_element.send_keys(value))
        return self

    def type(self, value: str):
        def _action(web_element: WebElement):
            web_element.clear()
            web_element.send_keys(value)
            assert web_element.get_attribute("value") == value

        self._action_sequence(_action)
        return self

    @property
    def expect(self):
        return UiElementAssertion(self)

    @property
    def wait_for(self):
        return UiElementAssertion(self, TestConfig(raise_exception=False))

    def clear(self):
        self._action_sequence(lambda web_element: web_element.clear())
        return self

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f"UiElement({self._by.__str__()})[{self._index}]"

    @property
    def list(self) -> "UiElementList":
        return UiElementList(self)

    def scroll_into_view(self, offset: Location = Location()):
        self._action_sequence(lambda web_element: script.scroll_to_center(self._webdriver, web_element, offset))

    def scroll_to_top(self, offset: Location = Location()):
        self._action_sequence(lambda web_element: script.scroll_to_top(self._webdriver, web_element, offset))

    def _count_elements(self):
        count = 0

        def _count(web_elements: List[WebElement]):
            nonlocal count
            count = len(web_elements)

        self._find_web_elements(_count)
        return count


class UiElementList(PageObjectList[UiElement]):

    def __init__(self, ui_element: UiElement):
        self._ui_element = ui_element

    def __iter__(self):
        for i in range(self._ui_element._count_elements()):
            yield self.__getitem__(i)

    def __getitem__(self, index: int):
        return UiElement(
            ui_element=self._ui_element._ui_element,
            webdriver=self._ui_element._webdriver,
            by=self._ui_element._by,
            parent=self._ui_element._parent,
            index=index
        )


A = TypeVar('A')


class UiElementAssertion:

    def __init__(
        self,
        ui_element: UiElement,
        config: TestConfig = TestConfig(),
    ):
        self._ui_element = ui_element
        self._config = config

    def _map_find(self, mapper: Callable[[WebElement], any]):
        value = None
        try:
            def _map_value(web_element: WebElement):
                nonlocal value
                value = mapper(web_element)

            self._ui_element._find_web_element(_map_value)

        except Exception as e:
            pass

        return value

    def _create_property_assertion(
        self,
        assertion_class: Type[A],
        mapper: Mapper[WebElement, any],
        property_name: str
    ) -> A:
        return assertion_class(
            parent=None,
            actual=lambda: self._map_find(mapper),
            subject=lambda: f"{self._ui_element.name}.{property_name} {Format.param(self._map_find(mapper))}",
            config=self._config,
        )

    @property
    def text(self):
        def _map(web_element: WebElement):
            return web_element.text

        return StringAssertion(
            parent=None,
            actual=lambda: self._map_find(_map),
            subject=lambda: f"{self._ui_element.name}.text {Format.param(self._map_find(_map))}",
            config=self._config,
        )

    @property
    def displayed(self):
        def _map(web_element: WebElement):
            return web_element.is_displayed()

        return self._create_property_assertion(BinaryAssertion, _map, "displayed")

    @property
    def enabled(self):
        def _map(web_element: WebElement):
            return web_element.is_enabled()

        return self._create_property_assertion(BinaryAssertion, _map, "enabled")

    @property
    def selected(self):
        def _map(web_element: WebElement):
            return web_element.is_selected()

        return self._create_property_assertion(BinaryAssertion, _map, "selected")

    def attribute(self, attribute: str):
        def _map(web_element: WebElement):
            return web_element.get_attribute(attribute)

        return self._create_property_assertion(StringAssertion, _map, f"attribute({attribute}")

    def css(self, property: str):
        def _map(web_element: WebElement):
            return web_element.value_of_css_property(property)

        return self._create_property_assertion(StringAssertion, _map, f"css({property}")

    @property
    def value(self):
        return self.attribute("value")

    @property
    def count(self):
        return QuantityAssertion(
            parent=None,
            actual=lambda: self._ui_element._count_elements(),
            subject=lambda: f"element count {Format.param(self._ui_element._count_elements())}",
            config=self._config
        )
