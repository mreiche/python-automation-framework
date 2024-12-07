import logging
import re
from abc import ABC
from typing import Generic, TypeVar

import inject

from paf.common import Rect, HasParent, HasName
from paf.control import RetryException, retry
from paf.types import Supplier, Predicate, Number, ACTUAL_TYPE, Mapper


class Format:
    @staticmethod
    def param(value: any):
        if value is None:
            return "*undefined*"
        else:
            return f"[{value}]"


class AssertionErrorWrapper(RetryException, AssertionError):
    pass


class AbstractAssertion(Generic[ACTUAL_TYPE], HasParent, ABC):
    def __init__(
        self,
        parent: None | HasName,
        actual_supplier: Supplier[ACTUAL_TYPE],
        name_supplier: Supplier[str],
        raise_exception: bool = True
    ):
        self._raise = raise_exception

        if parent and isinstance(parent, AbstractAssertion):
            self._raise = parent._raise

        self._parent = parent
        self._actual_supplier = actual_supplier
        self._name_supplier = name_supplier
        self._used = False

    @property
    def name(self):
        return self._name_supplier()

    @property
    def raise_exception(self):
        return self._raise

    def _find_closest_ui_element(self) -> "UiElement":
        from paf.uielement import UiElement
        ui_element = None

        def _find(inst: HasName):
            nonlocal ui_element
            if isinstance(inst, UiElement):
                ui_element = inst
                return False
            return True

        self._trace_path(_find)
        return ui_element

    def _test_sequence(
        self,
        test: Predicate[ACTUAL_TYPE],
        additional_subject: Supplier = None,
    ) -> bool:
        from paf.listener import Listener
        listener = inject.instance(Listener)

        try:
            def perform_test():
                assert test(self.actual), "Expected"

            retry(perform_test, lambda e: listener.assertion_failed(self, self._find_closest_ui_element(), e))
            listener.assertion_passed(self, self._find_closest_ui_element())
            return True

        except RetryException as exception:
            exception.add_subject(self.name_path)
            if additional_subject:
                exception.add_subject(additional_subject())
            #exception.update_sequence(sequence)
            listener.assertion_failed_finally(self, self._find_closest_ui_element(), exception)

            if self._raise:
                raise AssertionErrorWrapper(exception)
                #AssertionErrorWrapper(AssertionError(f"{exception.enclosed_exception} {subject}"), sequence)
            return False

    @property
    def actual(self) -> ACTUAL_TYPE:
        if not self._used:
            def _use(inst: HasName):
                if not isinstance(inst, AbstractAssertion):
                    return False

                inst._used = True
                return True
            self._trace_path(_use)

        return self._actual_supplier()

    def __del__(self):
        if not self._used:
            logging.warning(f"Unused Assertion: {self.name_path}")


ASSERTION = TypeVar('ASSERTION', bound=AbstractAssertion)


class BinaryAssertion(AbstractAssertion[ACTUAL_TYPE]):
    def be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual == expected, lambda: f"to be {Format.param(expected)}")

    def not_be(self, expected: any) -> bool:
        return self._test_sequence(lambda actual: actual != expected, lambda: f"not to be {Format.param(expected)}")


class QuantityAssertion(BinaryAssertion[ACTUAL_TYPE]):
    def map(self, mapper: Mapper):
        return self.__class__(
            parent=self,
            actual_supplier=lambda: mapper(self._actual_supplier()),
            name_supplier=lambda: f"mapped ",
        )

    def between(self, lower: Number, higher: Number):
        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: lower <= self._actual_supplier() <= higher,
            name_supplier=lambda: f"between {Format.param(lower)} and {Format.param(higher)} ",
        )

    def greater_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: self._actual_supplier() > expected,
            name_supplier=lambda: f"greater than {Format.param(expected)} ",
        )

    def lower_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: self._actual_supplier() < expected,
            name_supplier=lambda: f"lower than {Format.param(expected)} ",
        )

    def greater_equal_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: self._actual_supplier() >= expected,
            name_supplier=lambda: f"greater equal than {Format.param(expected)} ",
        )

    def lower_equal_than(self, expected: Number):
        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: self._actual_supplier() <= expected,
            name_supplier=lambda: f"lower equal than {Format.param(expected)} ",
        )


class StringAssertion(QuantityAssertion[str]):
    def starts_with(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: str(self._actual_supplier()).startswith(expected),
            name_supplier=lambda: f"starts with {Format.param(expected)} ",
        )

    def ends_with(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: str(self._actual_supplier()).endswith(expected),
            name_supplier=lambda: f"ends with {Format.param(expected)} ",
        )

    def contains(self, expected: str):
        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: str(self._actual_supplier()).find(expected) >= 0,
            name_supplier=lambda: f"contains {Format.param(expected)} ",
        )

    def matches(self, regex: str | re.Pattern):
        if not isinstance(regex, re.Pattern):
            regex = re.compile(regex, re.MULTILINE | re.IGNORECASE | re.UNICODE)

        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: regex.search(self._actual_supplier()) is not None,
            name_supplier=lambda: f"matches {Format.param(regex.pattern)} ",
        )

    def has_words(self, *words: any):
        pattern = "|".join(words)
        regex = re.compile(f"\\b(?:{pattern})\\b", re.MULTILINE | re.IGNORECASE | re.UNICODE)

        return BinaryAssertion(
            parent=self,
            actual_supplier=lambda: regex.search(self._actual_supplier()) is not None,
            name_supplier=lambda: f"has words {Format.param(pattern)} ",
        )

    @property
    def length(self):
        return QuantityAssertion(
            parent=self,
            actual_supplier=lambda: len(self._actual_supplier()),
            name_supplier=lambda: f"length {Format.param(len(self._actual_supplier()))} ",
        )


class RectAssertion(AbstractAssertion[Rect]):
    pass
