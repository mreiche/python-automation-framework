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

#
# class UiElementFinder:
#     @abstractmethod
#     def find(self, by: Locator) -> "UiElement":
#         pass


@dataclass()
class TestConfig:
    raise_exception: bool = False
    retry_count: int = 3
    wait_after_fail: float = 0.3
