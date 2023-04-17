from abc import abstractmethod, ABC
from typing import Callable, Type, TypeVar, List, Generic, Iterable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from core.assertion import StringAssertion, Format, BinaryAssertion, QuantityAssertion
from core.common import HasParent, TestConfig, Locator
from core.locator import By
from core.retry import Sequence
from core.types import Mapper
from core.xpath import XPath


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

    @property
    def first(self):
        return self.__getitem__(0)

    @property
    def last(self):
        return self.__getitem__(-1)


class PageObject(Generic[T]):
    @property
    @abstractmethod
    def list(self) -> PageObjectList[T]:
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
        return UiElement(by, ui_element=self, parent=self)

    def _find_web_elements(self) -> List[WebElement]:
        if self._ui_element:
            web_elements = self._ui_element._find_web_elements()
        elif self._webdriver:
            web_elements = self._webdriver.find_elements(self._by.by, self._by.value)
        else:
            raise Exception("UiElement initialized without WebDriver nor UiElement")

        if self._by.get_filter():
            web_elements = list(filter(self._by.get_filter(), web_elements))

        return web_elements

    def _find_web_element(self) -> WebElement:
        web_elements = self._find_web_elements()
        count = len(web_elements)

        if self._by.is_unique and count != 1:
            raise Exception(f"{self.name_path}: not unique")
        elif count > self._index:
            return web_elements[self._index]
        else:
            raise Exception(f"{self.name_path}: not found")

    def _action_sequence(self, cb: Callable):
        sequence = Sequence()

        exception = None
        passed = False

        def perform_action():
            nonlocal exception
            nonlocal passed

            try:
                cb()
                passed = True
            except Exception as e:
                exception = e
                passed = False

            return passed

        sequence.run(perform_action)

        if not passed:
            raise Exception(f"{exception} after {sequence.count} retries ({round(sequence.duration, 2)} seconds)")

    def click(self):
        self._action_sequence(lambda: self._find_web_element().click())
        return self

    def send_keys(self, value: str):
        self._action_sequence(lambda: self._find_web_element().send_keys(value))
        return self

    def type(self, value: str):
        def _input():
            web_element = self._find_web_element()
            web_element.clear()
            web_element.send_keys(value)
            assert web_element.get_attribute("value") == value

        self._action_sequence(_input)
        return self

    @property
    def expect(self):
        return UiElementAssertion(self)

    @property
    def wait_for(self):
        return UiElementAssertion(self, TestConfig(raise_exception=False))

    def clear(self):
        self._action_sequence(lambda: self._find_web_element().clear())
        return self

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f"UiElement({self._by.__str__()})[{self._index}]"

    @property
    def list(self):
        return UiElementList(self)


class UiElementList(PageObjectList[UiElement]):

    def __init__(self, ui_element: UiElement):
        self._ui_element = ui_element

    def __iter__(self):
        i = 0
        for _ in self._ui_element._find_web_elements():
            yield self.__getitem__(i)
            i += 1

    def __getitem__(self, index: int) -> UiElement:
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
        web_element = self._ui_element._find_web_element()
        try:
            return mapper(web_element)
        except Exception as e:
            return None

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
            actual=lambda: len(self._ui_element._find_web_elements()),
            subject=lambda: f"{self._ui_element.name} count",
            config=self._config
        )
