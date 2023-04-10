from typing import Callable

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from core.by import By
from core.page import Page
from core.retry import RetrySequence


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
        return self._by.__str__()


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

    def _sequenced(self, cb: Callable):
        sequence = RetrySequence()
        sequence.run(cb)

    def click(self) -> "UiElement":
        self._sequenced(lambda: self._core.find_web_element().click())
        return self

    def send_keys(self, value: str) -> "UiElement":
        self._sequenced(lambda: self._core.find_web_element().send_keys(value))
        return self

    def input(self, value: str):
        def _input():
            webelement = self._core.find_web_element()
            webelement.clear()
            webelement.send_keys(value)
            assert webelement.get_attribute("value") == value

        self._sequenced(_input)

    def clear(self) -> "UiElement":
        self._sequenced(lambda: self._core.find_web_element().clear())
        return self

    @property
    def name(self):
        return f"UiElement({self._core.__str__()})"

    def __str__(self):
        path = [self]
        inst = self
        while inst._parent:
            path.append(inst._parent)
            inst = inst._parent

        return " > ".join(map(str, reversed(path)))
