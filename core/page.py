from selenium.webdriver.remote.webdriver import WebDriver
from core.by import By


class Page:
    _title: str
    _url: str

    def __init__(self, webdriver: WebDriver):
        self._webdriver = webdriver

    def find(self, by: By) -> "UiElement":
        from core.uielement import UiElement
        return UiElement(self._webdriver, by, self)

    @property
    def webdriver(self):
        return self._webdriver

    def open(self, url: str):
        self._webdriver.get(url)
        self._url = self._webdriver.current_url
        self._title = self._webdriver.title

    def __str__(self):
        return f"Page({self._title, self._url})"
