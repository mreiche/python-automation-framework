import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import inject
from selenium.webdriver.remote.webelement import WebElement

from paf.locator import By
from paf.types import Predicate
from paf.xpath import XPath

Locator = By | XPath | str


class HasName(ABC):
    @property
    @abstractmethod
    def name(self):  # pragma: no cover
        pass


class HasParent(HasName, ABC):
    # @property
    # def _parent(self):
    #     return self.__parent
    #
    # @_parent.setter
    # def _parent(self, parent: "HasParent"):
    #     self.__parent = parent

    @property
    def name_path(self):
        from paf.component import Component
        from paf.page import Page
        from paf.uielement import UiElement
        name_path = ""

        def _trace(inst: HasName):
            nonlocal name_path
            name_path = inst.name + name_path
            if isinstance(inst, (UiElement, Component, Page)) \
                and isinstance(inst, HasParent) \
                and isinstance(inst._parent, (UiElement, Component, Page)):
                name_path = " > " + name_path
            return True

        self._trace_path(_trace)
        return name_path

    def _trace_path(self, consumer: Predicate[HasName]):
        inst = self
        while isinstance(inst, HasName):
            if not consumer(inst) or not isinstance(inst, HasParent):
                break

            inst = inst._parent


@dataclass()
class Point:
    x: float = 0
    y: float = 0


@dataclass()
class Size:
    width: float = 0
    height: float = 0


class Rect(Point, Size):

    @staticmethod
    def from_web_element(web_element: WebElement):
        rect = web_element.rect
        return Rect(rect["x"], rect["y"], rect["width"], rect["height"])

    def __init__(self, x: float = 0, y: float = 0, width: float = 0, height: float = 0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def left(self):
        return self.x

    @property
    def top(self):
        return self.y

    @property
    def right(self):
        return self.left + self.width

    @property
    def bottom(self):
        return self.top + self.height

    def contains(self, rect: "Rect"):
        return rect.left >= self.left \
            and rect.right <= self.right \
            and rect.top >= self.top \
            and rect.bottom <= self.bottom

    def intersects(self, rect: "Rect"):
        return rect.left <= self.right \
            and rect.right >= self.left \
            and rect.top <= self.bottom \
            and rect.bottom >= self.top


class Property(Enum):
    PAF_SCREENSHOTS_DIR = "screenshots"
    PAF_WINDOW_SIZE = "1920x1080"
    PAF_BROWSER_SETTING = "chrome"
    PAF_SEQUENCE_WAIT_AFTER_FAIL = 0.3
    PAF_SEQUENCE_RETRY_COUNT = 3
    PAF_SELENIUM_SERVER_URL = None
    PAF_DEMO_MODE = "0"
    PAF_DRIVER_PATH = None
    PAF_BINARY_PATH = None

    @staticmethod
    def env(prop: "Property") -> any:
        return os.getenv(prop.name, prop.value)


class Formatter:
    def datetime(self, date: datetime):
        return date.strftime('%Y-%m-%d-%H:%M:%S')


class NotFoundException(Exception):
    def __init__(self):
        super().__init__(f"Element not found")


class NotUniqueException(Exception):
    def __init__(self):
        super().__init__(f"Element not unique")


class WebdriverRetainer(ABC):
    @property
    @abstractmethod
    def webdriver(self):  # pragma: no cover
        pass


def inject_config(binder: inject.Binder):
    binder.bind(Formatter, Formatter())
