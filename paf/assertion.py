import logging
import re
from abc import ABC
from typing import TypeVar, Generic

import inject

from paf.common import Rect, HasParent
from paf.control import Control, RetryException
from paf.types import Supplier, Predicate, Number, Mapper

ACTUAL_TYPE = TypeVar("ACTUAL_TYPE")


class Format:
    @staticmethod
    def param(value: any):
        if value is None:
            return "*undefined*"
        else:
            return f"[{value}]"


class AbstractAssertion(Generic[ACTUAL_TYPE], HasParent, ABC):
    def __init__(
        self,
        parent: None | HasParent,
        actual: Supplier[ACTUAL_TYPE],
        name: Supplier[str],
        raise_exception: bool = True
    ):
        self._raise = raise_exception

        if parent and isinstance(parent, AbstractAssertion):
            self._raise = parent._raise

        self._parent = parent
        self._actual = actual
        self._name = name
        self._tested = False

    @property
    def name(self):
        return self._name()

    def _test_sequence(
        self,
        test: Predicate[ACTUAL_TYPE],
        additional_subject: Supplier = None,
    ) -> bool:
        self._tested = True
        from paf.listener import Listener

        control = inject.instance(Control)
        listener = inject.instance(Listener)

        try:
            def perform_test():
                assert test(self._actual())

            control.retry(perform_test, lambda e: listener.assertion_failed(self, e))
            listener.assertion_passed(self)
            return True

        except RetryException as e:
            listener.assertion_failed_finally(self, e)

            if self._raise:
                subject = self.name_path

                if additional_subject:
                    subject += additional_subject()

                raise AssertionError(f"Expected {subject} after {e.sequence.count} retries ({round(e.sequence.duration, 2)} seconds)")
            return False

    @property
    def actual(self) -> ACTUAL_TYPE:
        return self._actual()


class BinaryAssertion(AbstractAssertion[ACTUAL_TYPE]):
    def be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual == expected, lambda: f" to be {Format.param(expected)}")

    def __del__(self):
        if not self._tested:
            logging.error(f"{self.name_path} without tested expectation")


class QuantityAssertion(Generic[ACTUAL_TYPE], BinaryAssertion[ACTUAL_TYPE]):
    def map(self, mapper: Mapper):
        return self.__class__(
            parent=self,
            actual=lambda: mapper(self._actual()),
            name=lambda: "mapped",
        )

    def not_be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual != expected, lambda: f" not to be {Format.param(expected)}")

    def between(self, lower: Number, higher: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: lower <= self._actual() <= higher,
            name=lambda: f"between {Format.param(lower)} and {Format.param(higher)}",
        )

    def greater_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() > expected,
            name=lambda: f"greater than {Format.param(expected)}",
        )

    def lower_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() < expected,
            name=lambda: f"lower than {Format.param(expected)}",
        )

    def greater_equal_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() >= expected,
            name=lambda: f"greater equal than {Format.param(expected)}",
        )

    def lower_equal_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() <= expected,
            name=lambda: f"lower equal than {Format.param(expected)}",
        )


class StringAssertion(QuantityAssertion[str]):
    def starts_with(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).startswith(expected),
            name=lambda: f"starts with {Format.param(expected)}",
        )

    def ends_with(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).endswith(expected),
            name=lambda: f"ends with {Format.param(expected)}",
        )

    def contains(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).find(expected) >= 0,
            name=lambda: f"contains {Format.param(expected)}",
        )

    def matches(self, regex: str | re.Pattern):
        if not isinstance(regex, re.Pattern):
            regex = re.compile(regex, re.MULTILINE | re.IGNORECASE | re.UNICODE)

        return BinaryAssertion(
            parent=self,
            actual=lambda: regex.search(self._actual()) is not None,
            name=lambda: f"matches {Format.param(regex.pattern)}",
        )

    def has_words(self, *words: any):
        pattern = "|".join(words)
        regex = re.compile(f"\\b(?:{pattern})\\b", re.MULTILINE | re.IGNORECASE | re.UNICODE)

        return BinaryAssertion(
            parent=self,
            actual=lambda: regex.search(self._actual()) is not None,
            name=lambda: f"has words {Format.param(pattern)}",
        )

    @property
    def length(self):
        return QuantityAssertion(
            parent=self,
            actual=lambda: len(self._actual()),
            name=lambda: f"length {Format.param(len(self._actual()))}",
        )


class RectAssertion(AbstractAssertion[Rect]):
    pass
