from typing import Callable

from paf.control import Config, Sequence
from paf.types import Supplier, Predicate, Number
import re


class Format:
    @staticmethod
    def param(value: any):
        if value is None:
            return "[null]"
        else:
            return f"[{value}]"

    @staticmethod
    def separate(*args):
        return " ".join(map(str, args))


class AbstractPropertyAssertion:
    def __init__(
        self,
        parent: None | object,
        actual: Supplier[any],
        subject: Supplier[str],
        config: Config = None,
        failed: Callable = None,
        passed: Callable = None,
        failed_finally: Callable = None
    ):
        if parent:
            assert isinstance(parent, AbstractPropertyAssertion)
            if not config:
                config = parent._config

        if not config:
            config = Config()

        self._parent = parent
        self._actual = actual
        self._config = config
        self._subject = subject
        self._failed = failed
        self._passed = passed
        self._failed_finally = failed_finally

    def _test_sequence(
        self,
        test: Predicate[any],
        additional_subject: Supplier = None,
    ) -> bool:

        sequence = Sequence(retry_count=self._config.retry_count, wait_after_fail=self._config.wait_after_fail)
        exception = None

        def perform_test():
            nonlocal exception

            try:
                assert test(self._actual())
                if self._passed:
                    self._passed()
                exception = None
            except Exception as e:
                if self._failed:
                    self._failed()
                exception = e

            return not exception

        sequence.run(perform_test)

        if exception:
            if self._failed_finally:
                self._failed_finally()

            if self._config.raise_exception:
                subject = self._create_subject()
                if additional_subject:
                    subject += additional_subject()

                raise AssertionError(f"Expected {subject} after {sequence.count} retries ({round(sequence.duration, 2)} seconds)")

        return not exception

    def _create_subject(self) -> str:
        path = [self]
        inst = self
        while inst._parent:
            path.append(inst._parent)
            inst = inst._parent

        return " ".join(map(lambda x: x._subject(), reversed(path)))

    @property
    def actual(self):
        return self._actual()


class BinaryAssertion(AbstractPropertyAssertion):
    def be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual == expected, lambda: f" to be {Format.param(expected)}")


class QuantityAssertion(BinaryAssertion):

    def not_be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual != expected, lambda: f" not to be {Format.param(expected)}")

    def between(self, lower: Number, higher: Number):
        return BinaryAssertion(
            parent=self,
            actual=lambda: lower <= self._actual() <= higher,
            subject=lambda: f"between {Format.param(lower)} and {Format.param(higher)}",
        )

    def greater_than(self, expected: Number) -> BinaryAssertion:
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() > expected,
            subject=lambda: f"greater than {Format.param(expected)}",
        )

    def lower_than(self, expected: Number) -> BinaryAssertion:
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() < expected,
            subject=lambda: f"lower than {Format.param(expected)}",
        )

    def greater_equal_than(self, expected: Number) -> BinaryAssertion:
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() >= expected,
            subject=lambda: f"greater equal than {Format.param(expected)}",
        )

    def lower_equal_than(self, expected: Number) -> BinaryAssertion:
        return BinaryAssertion(
            parent=self,
            actual=lambda: self._actual() <= expected,
            subject=lambda: f"lower equal than {Format.param(expected)}",
        )


class StringAssertion(QuantityAssertion):
    def starts_with(self, expected: str) -> BinaryAssertion:
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).startswith(expected),
            subject=lambda: f"starts with {Format.param(expected)}",
        )

    def ends_with(self, expected: str) -> BinaryAssertion:
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).endswith(expected),
            subject=lambda: f"ends with {Format.param(expected)}",
        )

    def contains(self, expected: str) -> BinaryAssertion:
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).find(expected) >= 0,
            subject=lambda: f"contains {Format.param(expected)}",
        )

    def matches(self, expected: str | re.Pattern) -> BinaryAssertion:
        if not isinstance(expected, re.Pattern):
            expected = re.compile(expected, re.MULTILINE | re.IGNORECASE | re.UNICODE)

        return BinaryAssertion(
            parent=self,
            actual=lambda: expected.match(self._actual()) is not None,
            subject=lambda: f"matches {Format.param(expected)}",
        )

    @property
    def length(self) -> QuantityAssertion:
        return QuantityAssertion(
            parent=self,
            actual=lambda: len(self._actual()),
            subject=lambda: f"length {Format.param(len(self._actual()))}",
        )
