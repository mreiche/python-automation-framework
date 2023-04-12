from typing import Callable, Type, TypeVar

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from core.assertion import StringAssertion, Format, BinaryAssertion
from core.by import By
from core.config import TestConfig
from core.retry import Sequence
from core.types import Mapper

T = TypeVar('T')


class UiElementCore:
    def __init__(
        self,
        finder: WebElement | WebDriver,
        by: By
    ):
        self._finder = finder
        self._by = by

    def find_web_element(self) -> WebElement:
        web_elements = self._finder.find_elements(self._by.by, self._by.value)

        if self._by.get_filter():
            web_elements = list(filter(self._by.get_filter(), web_elements))

        count = len(web_elements)
        if self._by.is_unique and count != 1:
            raise Exception(f"{self}: Element not unique")
        elif count > 0:
            return web_elements[0]
        else:
            raise Exception(f"{self}: Element not found")

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f"UiElement({self._by.__str__()})"


class UiElement:

    _core: UiElementCore

    def __init__(
        self,
        finder: WebElement | WebDriver,
        by: By,
        parent: object = None
    ):
        self._core = UiElementCore(finder, by)
        self._parent = parent

    def find(self, by: By) -> "UiElement":
        return UiElement(self._core.find_web_element(), by, self)

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
            raise Exception(f"{self.name_path} {exception} after {sequence.count} retries ({round(sequence.duration, 2)} seconds)")

    def click(self) -> "UiElement":
        self._action_sequence(lambda: self._core.find_web_element().click())
        return self

    def send_keys(self, value: str) -> "UiElement":
        self._action_sequence(lambda: self._core.find_web_element().send_keys(value))
        return self

    def test(self):
        # self._core.find_web_element().
        pass

    def input(self, value: str) -> "UiElement":
        def _input():
            web_element = self._core.find_web_element()
            web_element.clear()
            web_element.send_keys(value)
            assert web_element.get_attribute("value") == value

        self._action_sequence(_input)
        return self

    @property
    def expect(self):
        return UiElementAssertion(self._core, self)

    @property
    def wait_for(self):
        return UiElementAssertion(self._core, self, TestConfig(raise_exception=False))

    def clear(self) -> "UiElement":
        self._action_sequence(lambda: self._core.find_web_element().clear())
        return self

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self._core.name

    @property
    def name_path(self):
        path = [self]
        inst = self
        while inst._parent:
            path.append(inst._parent)
            inst = inst._parent

        return " > ".join(map(str, reversed(path)))


class UiElementAssertion:

    def __init__(
        self,
        core: UiElementCore,
        ui_element: UiElement,
        config: TestConfig = TestConfig(),
    ):
        self._core = core
        self._ui_element = ui_element
        self._config = config

    def _map_find(self, mapper: Callable[[WebElement], any]):
        web_element = self._core.find_web_element()
        try:
            return mapper(web_element)
        except Exception as e:
            return None

    def _create_property_assertion(
        self,
        assertion_class: Type[T],
        mapper: Mapper[WebElement, any],
        property_name: str
    ) -> T:
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
