import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import inject
from selenium.webdriver.remote.webelement import WebElement

from paf.locator import By
from paf.xpath import XPath

Locator = By | XPath | str


class HasName(ABC):
    @property
    @abstractmethod
    def name(self):
        pass


class HasParent(HasName, ABC):
    @property
    def _parent(self):
        return self.__parent

    @_parent.setter
    def _parent(self, parent: "HasParent"):
        self.__parent = parent

    @property
    def name_path(self):
        path = [self]
        inst = self
        while hasattr(inst, "_parent") and inst._parent:
            path.append(inst._parent)
            inst = inst._parent

        return " > ".join(map(str, reversed(path)))


@dataclass()
class Point:
    x: int = 0
    y: int = 0


@dataclass()
class Size:
    width: int = 0
    height: int = 0


class Rect(Point, Size):

    @staticmethod
    def from_web_element(web_element: WebElement):
        rect = web_element.rect
        return Rect(rect["x"], rect["y"], rect["width"], rect["height"])

    def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
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

    @staticmethod
    def env(prop: "Property") -> any:
        return os.getenv(prop.name, prop.value)


class Formatter:
    def datetime(self, date: datetime):
        return date.strftime('%Y-%m-%d-%H:%M:%S')


def inject_config(binder: inject.Binder):
    binder.bind(Formatter, Formatter())
