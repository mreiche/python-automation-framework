from selenium.webdriver.common.by import By as SeleniumBy


class By:
    def __init__(self, by: SeleniumBy, value: str):
        self.by = by
        self.value = value
        self._unique = False

    def unique(self) -> "By":
        self._unique = True
        return self

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
        return f"By.{self.by}({self.value})"
