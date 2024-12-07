import pytest

from paf.common import RetryException, Sequence
from paf.uielement import InexistentUiElement


def test_assertion_error_label():
    with pytest.raises(AssertionError, match="Expected"):
        assert False, "Expected"


def test_catch_assertion_error():
    inexistent_ui_element = InexistentUiElement()
    with pytest.raises(AssertionError):
        inexistent_ui_element.expect.count.be(1)


def test_nested_retry_exception_message():
    exception = Exception("nested")
    sequence = Sequence()
    a = RetryException(exception, sequence)
    b = RetryException(a, sequence)
    b._count = 99
    b._duration = 2

    try:
        raise b
    except Exception as e:
        assert f"{e}" == "nested after 99 retries (2 seconds)"
