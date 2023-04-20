from abc import ABC, abstractmethod
from dataclasses import dataclass

from paf.locator import By
from paf.xpath import XPath

Locator = By | XPath


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
class TestConfig:
    raise_exception: bool = True
    retry_count: int = 3
    wait_after_fail: float = 0.3


@dataclass()
class Point:
    x: int = 0
    y: int = 0


@dataclass()
class Size:
    width: int = 0
    height: int = 0


class Rect(Point, Size):

    def __init__(self, x: int = 0, y:int = 0, width: int = 0, height: int = 0):
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
        return rect.left >= self.right \
               or rect.right <= self.left \
               or rect.top >= self.bottom \
               or rect.bottom <= self.top
