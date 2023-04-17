from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.remote.webelement import WebElement

from core.dom import Attribute
from core.types import Predicate


class By:
    def __init__(self, by: SeleniumBy, value: str):
        self._by = by
        self._value = value
        self._unique = False
        self._filter = None

    @property
    def by(self):
        return self._by

    @property
    def value(self):
        return self._value

    def _copy(self):
        by = By(self._by, self._value)
        by._unique = self._unique
        by._filter = self._filter
        return by

    @property
    def unique(self):
        by = self._copy()
        by._unique = True
        return by

    def filter(self, filter: Predicate[WebElement]):
        by = self._copy()
        by._filter = filter
        return by

    @property
    def displayed(self):
        def _displayed(webelement: WebElement):
            return webelement.is_displayed()

        return self.filter(_displayed)

    def get_filter(self):
        return self._filter

    @property
    def is_unique(self):
        return self._unique

    @staticmethod
    def id(id: str):
        return By(SeleniumBy.ID, id)

    @staticmethod
    def xpath(xpath: str):
        return By(SeleniumBy.XPATH, xpath)

    @staticmethod
    def name(name: str):
        return By(SeleniumBy.NAME, name)

    @staticmethod
    def class_name(class_name: str):
        return By(SeleniumBy.CLASS_NAME, class_name)

    @staticmethod
    def tag_name(tag_name: str):
        return By(SeleniumBy.TAG_NAME, tag_name)

    @staticmethod
    def css_selector(selector: str):
        return By(SeleniumBy.CSS_SELECTOR, selector)

    def __str__(self) -> str:
        id = f"By.{self._by}({self._value})"
        if self._filter:
            id += " filtered"
        return id

    def to_xpath(self):
        from core.xpath import XPath

        if self._by.XPATH:
            return XPath.at(self._value)
        elif self._by.NAME:
            return XPath.at("//*").attribute(Attribute.NAME).be(self._value)
        elif self._by.CLASS_NAME:
            return XPath.at("//*").attribute(Attribute.CLASS).be(self._value)
        elif self._by.ID:
            return XPath.at("//*").attribute(Attribute.ID).be(self._value)
        elif self._by.CLASS_NAME:
            return XPath.at(self._value)
        else:
            raise Exception(f"By type '{self.by}' not supported (yet)")
