import re
from typing import List, Iterable

from core.by import By


class XPath:

    def __init__(self, selector: str, position: int = None):
        self._selector = selector
        if position and position == 0:
            position = 1
        self._pos = position
        self._root: XPath = None
        self._parent: XPath = None
        self._sub: XPath = None
        self._encloses: List[XPath] = []
        self._attributes: List[str] = []

    class Test:
        def __init__(self, xpath: "XPath", attribute: str):
            self._xpath = xpath
            self._attribute = attribute

        def be(self, value: any):
            self._attribute_is(self._attribute, value)
            return self._xpath

        @property
        def present(self):
            self._xpath._attributes.append(self._attribute)
            return self._xpath

        def contains(self, value: any):
            self._attribute_matches("contains", self._attribute, value)
            return self._xpath

        def has_words(self, *words: any):
            if not isinstance(words, Iterable):
                words = [words]
            self._attribute_contains_words(self._attribute, words)
            return self._xpath

        def starts_with(self, value: any):
            self._attribute_matches("starts-with", self._attribute, value)
            return self._xpath

        def ends_with(self, value: any):
            self._attribute_matches("ends-with", self._attribute, value)
            return self._xpath

        def _attribute_is(self, attribute: str, value: any):
            self._xpath._attributes.append(XPath.something_is(attribute, value))

        def _attribute_matches(self, operation: str, attribute: str, value: any):
            self._xpath._attributes.append(XPath.something_matches(operation, attribute, value))

        def _attribute_contains_words(self, attribute: str, value: Iterable[any]):
            for word in value:
                self._xpath._attributes.append(XPath.something_contains_word(attribute, word))

    @staticmethod
    def _normalize_selector(selector: any) -> str:
        if isinstance(selector, By):
            selector = selector.to_xpath()

        if isinstance(selector, XPath):
            selector = selector._build()

        return selector

    @staticmethod
    def at(selector: str, position: int = None):
        selector = XPath._normalize_selector(selector)
        xpath = XPath(XPath._translate_sub_selection(selector), position)
        xpath._root = xpath
        xpath._parent = xpath
        return xpath

    def select(self, selector: str, position: int = None):
        selector = XPath._normalize_selector(selector)
        xpath = XPath(XPath._translate_sub_selection(selector), position)
        xpath._root = self._root
        self._parent._sub = xpath
        xpath._parent = xpath
        return xpath

    def encloses(self, selector: str, position: int = None):
        selector = XPath._normalize_selector(selector)
        xpath = XPath(XPath._translate_inner_selection(selector), position)
        xpath._root = self._root
        xpath._parent = self._parent
        self._encloses.append(xpath)
        return xpath

    @staticmethod
    def _is_function(attribute: str):
        return attribute.strip().endswith(")")

    def attribute(self, attribute: str):
        if not XPath._is_function(attribute):
            attribute = f"@{attribute}"

        return XPath.Test(self, attribute)

    def classes(self, *classes: any):
        if not isinstance(classes, Iterable):
            classes = [classes]

        return self.attribute("class").has_words(classes)

    @property
    def text(self):
        return XPath.Test(self, ".//text()")

    @staticmethod
    def _translate_sub_selection(selector: str):
        selector = selector.strip()

        if selector.startswith("("):
            return selector
        elif selector.startswith("./"):
            selector = selector.replace("./", "/", 1)
        elif not selector.startswith("/"):
            selector = f"//{selector}"

        return selector

    @staticmethod
    def _translate_inner_selection(selector: str):
        selector = selector.strip()
        if selector.startswith("//"):
            return re.sub("^//", "descendant::", selector)
        elif selector.startswith("/"):
            return re.sub("^/", "child::", selector)
        elif selector.startswith("./"):
            return re.sub("^\\./", "child::", selector)
        else:
            return f"descendant::{selector}"

    @staticmethod
    def something_contains_word(something: str, string: any):
        return f"contains(concat(' ', normalize-space({something}), ' '), ' {string} ')"

    @staticmethod
    def something_is(something: str, value: any):
        return f"{something}='{value}'"

    @staticmethod
    def something_is_not(something: str, value: any):
        return f"{something}!='{value}'"

    @staticmethod
    def something_matches(operation:str, something: str, value: any):
        return f"{operation}({something},'{value}')"

    def _build(self):
        xpath = self._selector
        attributes = self._attributes.copy()
        for encloses in self._encloses:
            attributes.append(encloses._build())

        if len(attributes) > 0:
            xpath += f"[{' and '.join(attributes)}]"

        if self._pos:
            if self._pos < 0:
                xpath += "[last()]"
            elif self._pos != 0:
                xpath += f"[{self._pos}]"

        if self._sub:
            xpath += self._sub._build()

        return xpath

    def __str__(self):
        return self._root._build()
