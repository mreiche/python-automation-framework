from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.remote.webelement import WebElement

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

    def _copy(self) -> "By":
        by = By(self._by, self._value)
        by._unique = self._unique
        by._filter = self._filter
        return by

    @property
    def unique(self) -> "By":
        by = self._copy()
        by._unique = True
        return by

    def filter(self, filter: Predicate[WebElement]) -> "By":
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
    def id(id: str) -> "By":
        return By(SeleniumBy.ID, id)

    @staticmethod
    def xpath(xpath: str) -> "By":
        return By(SeleniumBy.XPATH, xpath)

    @staticmethod
    def name(name: str) -> "By":
        return By(SeleniumBy.NAME, name)

    @staticmethod
    def class_name(class_name: str) -> "By":
        return By(SeleniumBy.CLASS_NAME, class_name)

    def __str__(self) -> str:
        id = f"By.{self._by}({self._value})"
        if self._filter:
            id += " filtered"
        return id
