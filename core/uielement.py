from typing import Callable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from core.assertion import StringAssertion, Supplier, Format
from core.by import By
from core.page import Page
from core.retry import Sequence


class UiElementCore:
    def __init__(
        self,
        finder: WebElement|WebDriver,
        by: By
    ):
        self._finder = finder
        self._by = by

    def find_web_element(self) -> WebElement:
        elements = self._finder.find_elements(self._by.by, self._by.value)
        count = len(elements)
        if self._by.is_unique and count != 1:
            raise Exception(f"{self}: Element not unique")
        elif count > 0:
            return elements[0]
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
        finder: WebElement|WebDriver,
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

    def input(self, value: str) -> "UiElement":
        def _input():
            webelement = self._core.find_web_element()
            webelement.clear()
            webelement.send_keys(value)
            assert webelement.get_attribute("value") == value

        self._action_sequence(_input)
        return self

    @property
    def expect(self):
        return UiElementAssertion(self._core, self, raise_exceptions=True)

    @property
    def wait_for(self):
        return UiElementAssertion(self._core, self, raise_exceptions=False)

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

    def __init__(self,
                 core: UiElementCore,
                 ui_element: UiElement,
                 raise_exceptions: bool = False
                 ):
        self._core = core
        self._ui_element = ui_element
        self._raise = raise_exceptions

    def _map_find(self, mapper: Callable[[WebElement], any]):
        try:
            web_element = self._core.find_web_element()
            return mapper(web_element)
        except Exception as e:
            return None

    @property
    def text(self):
        def map(web_element: WebElement):
            return web_element.text

        return StringAssertion(
            parent=None,
            actual=lambda: self._map_find(map),
            subject=lambda: f"{self._ui_element.name}.text {Format.param(self._map_find(map))}",
            raise_exceptions=self._raise,
        )
