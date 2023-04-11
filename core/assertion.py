from typing import Callable

from core.retry import Sequence

#T = TypeVar()
Predicate = Callable[[any], bool]
Supplier = Callable[[], any]

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
        actual: Supplier,
        subject: Callable[[], str],
        raise_exceptions: bool = False,
        failed: Callable = None,
        passed: Callable = None,
        failed_finally: Callable = None
    ):
        if parent:
            assert isinstance(parent, AbstractPropertyAssertion)

        self._parent = parent
        self._actual = actual
        self._raise = raise_exceptions
        self._subject = subject
        self._failed = failed
        self._passed = passed
        self._failed_finally = failed_finally

    def _test_sequence(
        self,
        test: Predicate,
        additional_subject: Supplier = None,
    ):

        sequence = Sequence()
        exception = None
        passed = False

        def perform_test():
            nonlocal exception
            nonlocal passed

            try:
                assert test(self._actual())
                if self._passed:
                    self._passed()
                passed = True
            except Exception as e:
                if self._failed:
                    self._failed()
                exception = e
                passed = False

            return passed

        sequence.run(perform_test)

        if not passed:

            if self._failed_finally:
                self._failed_finally()

            if self._raise:
                subject = self._create_subject()
                if additional_subject:
                    subject += additional_subject()

                raise AssertionError(f"{subject} after {sequence.count} retries ({round(sequence.duration, 2)} seconds)")

        return passed

    def _create_subject(self) -> str:
        path = [self]
        inst = self
        while inst._parent:
            path.append(inst._parent)
            inst = inst._parent

        return " ".join(map(lambda x: x._subject(), reversed(path)))


class BinaryAssertion(AbstractPropertyAssertion):
    def be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual == expected, lambda: f" expected {expected}")

    def not_be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual != expected, lambda: f" expected not {expected}")


class StringAssertion(BinaryAssertion):
    def startswith(self, expected: str) -> BinaryAssertion:
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).startswith(expected),
            subject=lambda: f"startswith {Format.param(expected)}",
            raise_exceptions=self._raise,
        )

    def endswith(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).endswith(expected),
            subject=lambda: f"endswith {Format.param(expected)}",
            raise_exceptions=self._raise,
        )

    def contains(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual=lambda: str(self._actual()).index(expected) != -1,
            subject=lambda: f"contains {Format.param(expected)}",
            raise_exceptions=self._raise,
        )

    def matches(self, expected: str):
        pass
