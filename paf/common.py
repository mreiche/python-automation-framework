import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from time import sleep, time
from typing import Callable, Optional
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
    @property
    @abstractmethod
    def _parent(self):  # pragma: no cover
        pass

    @_parent.setter
    @abstractmethod
    def _parent(self, parent: "HasParent"):  # pragma: no cover
        pass

    @property
    def name_path(self):
        from paf.component import Component
        from paf.page import Page
        from paf.uielement import UiElement
        name_path = ""

        def _trace(inst: HasParent):
            nonlocal name_path
            name_path = inst.name + name_path
            if isinstance(inst, (UiElement, Component, Page)) \
                and isinstance(inst, HasParent) \
                and isinstance(inst._parent, (UiElement, Component, Page)):
                name_path = " > " + name_path
            return True

        self._trace_path(_trace)
        return name_path

    def _trace_path(self, consumer: Predicate["HasParent"]):
        inst = self
        while isinstance(inst, HasParent):
            if consumer(inst) is False or not isinstance(inst, HasParent):
                break

            inst = inst._parent

    def get_path(self) -> list["HasParent"]:
        path = []
        self._trace_path(path.append)
        return path


@dataclass()
class Point:
    x: float = 0
    y: float = 0

    def add(self, point: "Point"):
        self.x += point.x
        self.y += point.y


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
        super().__init__(f"Not found")


class NotUniqueException(Exception):
    def __init__(self):
        super().__init__(f"Not unique")


class WebdriverRetainer(ABC):
    @property
    @abstractmethod
    def webdriver(self):  # pragma: no cover
        pass


class SubjectException(Exception):

    def __init__(self, exception: Exception):
        # if isinstance(exception, EncloseException):
        #     self._enclosed_exception = exception._enclosed_exception
        # else:
        self._subjects = []
        if isinstance(exception, SubjectException):
            self._subjects.extend(exception._subjects)
        else:
            self.add_subject(f"{exception}")
        #self._enclosed_exception = exception

    def add_subject(self, subject: str):
        self._subjects.append(subject)

    #@property
    #def enclosed_exception(self):
        #return self._enclosed_exception


class Sequence:
    def __init__(self, retry_count: int = 3, wait_after_fail: float = 0.2):
        self._max = retry_count
        self._wait = wait_after_fail
        self._count = 0
        self._start_time = 0

    def run(self, sequence: Callable[[], bool]):
        self._start_time = time()
        while True:
            if sequence() or self._count >= self._max:
                break

            self._count += 1
            sleep(self._wait)

    @property
    def duration(self):
        return time() - self._start_time

    @property
    def count(self):
        return self._count


class RetryException(SubjectException):
    def __init__(self, exception: Exception, sequence: Sequence = None):
        super().__init__(exception)

        if sequence:
            self._count = sequence.count
            self._duration = sequence.duration
        elif isinstance(exception, RetryException):
            self._count = exception._count
            self._duration = exception._duration
        #self.update_sequence(sequence)

    #def update_sequence(self, sequence: Sequence):

    def __str__(self):
        #prefix = f"{self._enclosed_exception}"
        prefix = " ".join(self._subjects)
        if len(prefix) > 0:
            prefix += " "
        return f"{prefix}after {self._count} retries ({round(self._duration, 2)} seconds)"


def inject_config(binder: inject.Binder):
    binder.bind(Formatter, Formatter())
