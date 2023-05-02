import re
from typing import Callable, Iterable, TypeVar, Generic

import inject

from paf.common import Rect
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
    #
    # @staticmethod
    # def separate(*args):
    #     return " ".join(map(str, args))


class AbstractPropertyAssertion(Generic[ACTUAL_TYPE]):
    def __init__(
        self,
        parent: None | object,
        actual: Supplier[ACTUAL_TYPE],
        subject: Supplier[str],
        raise_exception: bool = True,
        failed: Callable = None,
        passed: Callable = None,
        failed_finally: Callable = None
    ):
        self._raise = raise_exception

        if parent:
            assert isinstance(parent, AbstractPropertyAssertion)
            self._raise = parent._raise

        self._parent = parent
        self._actual = actual
        self._subject = subject
        self._failed = failed
        self._passed = passed
        self._failed_finally = failed_finally

    def _test_sequence(
        self,
        test: Predicate[ACTUAL_TYPE],
        additional_subject: Supplier = None,
    ) -> bool:

        control = inject.instance(Control)
        try:
            def perform_test():
                assert test(self._actual())

            control.retry(perform_test, self._failed)

            if self._passed:
                self._passed()
            return True

        except RetryException as e:
            if self._failed_finally:
                self._failed_finally()

            if self._raise:
                subject = self._create_subject()
                if additional_subject:
                    subject += additional_subject()

                raise AssertionError(f"Expected {subject} after {e.sequence.count} retries ({round(e.sequence.duration, 2)} seconds)")
            return False

    def _create_subject(self) -> str:
        path = [self]
        inst = self
        while inst._parent:
            path.append(inst._parent)
            inst = inst._parent

        return " ".join(map(lambda x: x._subject(), reversed(path)))

    @property
    def actual(self) -> ACTUAL_TYPE:
        return self._actual()


class BinaryAssertion(AbstractPropertyAssertion[ACTUAL_TYPE]):
    def be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual == expected, lambda: f" to be {Format.param(expected)}")


class QuantityAssertion(Generic[ACTUAL_TYPE], BinaryAssertion[ACTUAL_TYPE]):
    def map(self, mapper: Mapper):
        return self.__class__(
            parent=self,
            actual=lambda: mapper(self._actual()),
            subject=lambda: "mapped",
        )

    def not_be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual != expected, lambda: f" not to be {Format.param(expected)}")

    def between(self, lower: Number, higher: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: lower <= self._actual() <= higher,
            subject=lambda: f"between {Format.param(lower)} and {Format.param(higher)}",
        )

    def greater_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() > expected,
            subject=lambda: f"greater than {Format.param(expected)}",
        )

    def lower_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() < expected,
            subject=lambda: f"lower than {Format.param(expected)}",
        )

    def greater_equal_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() >= expected,
            subject=lambda: f"greater equal than {Format.param(expected)}",
        )

    def lower_equal_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() <= expected,
            subject=lambda: f"lower equal than {Format.param(expected)}",
        )


class StringAssertion(QuantityAssertion[str]):
    def starts_with(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).startswith(expected),
            subject=lambda: f"starts with {Format.param(expected)}",
        )

    def ends_with(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).endswith(expected),
            subject=lambda: f"ends with {Format.param(expected)}",
        )

    def contains(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).find(expected) >= 0,
            subject=lambda: f"contains {Format.param(expected)}",
        )

    def matches(self, regex: str | re.Pattern):
        if not isinstance(regex, re.Pattern):
            regex = re.compile(regex, re.MULTILINE | re.IGNORECASE | re.UNICODE)

        return BinaryAssertion(
            parent=self,
            actual=lambda: regex.search(self._actual()) is not None,
            subject=lambda: f"matches {Format.param(regex.pattern)}",
        )

    def has_words(self, *words: any):
        # if not isinstance(words, Iterable):
        #     words = [words]

        pattern = "|".join(words)
        regex = re.compile(f"\\b(?:{pattern})\\b", re.MULTILINE | re.IGNORECASE | re.UNICODE)

        return BinaryAssertion(
            parent=self,
            actual=lambda: regex.search(self._actual()) is not None,
            subject=lambda: f"has words {Format.param(pattern)}",
        )

    @property
    def length(self):
        return QuantityAssertion(
            parent=self,
            actual=lambda: len(self._actual()),
            subject=lambda: f"length {Format.param(len(self._actual()))}",
        )


class RectAssertion(AbstractPropertyAssertion[Rect]):
    pass
