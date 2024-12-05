import pytest

from paf.common import RetryException
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
    a = RetryException(exception, count=10, duration=99)
    b = RetryException(a, count=99, duration=2)

    try:
        raise b
    except Exception as e:
        assert  f"{e}" == "nested after 99 retries (2 seconds)"
