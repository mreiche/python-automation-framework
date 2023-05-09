from typing import Callable, TypeVar

T = TypeVar('T')
R = TypeVar('R')
Predicate = Callable[[T], bool]
Supplier = Callable[[], T]
Mapper = Callable[[T], R]
Number = float | int
Consumer = Callable[[T], None]
COMPONENT = TypeVar("COMPONENT")
PAGE = TypeVar("PAGE")
ACTUAL_TYPE = TypeVar("ACTUAL_TYPE")
