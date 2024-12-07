import dataclasses
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from time import sleep, time
from typing import Callable, Optional

from paf.common import Property, RetryException, Sequence
from paf.types import Consumer


@dataclass()
class Config(threading.local):
    retry_count: int = Property.env(Property.PAF_SEQUENCE_RETRY_COUNT)
    wait_after_fail: float = Property.env(Property.PAF_SEQUENCE_WAIT_AFTER_FAIL)


__config = Config()


def get_config():
    return __config


def __set_config(config: Config):
    global __config
    __config = config


@contextmanager
def change(
    retry_count: int = None,
    wait_after_fail: float = None,
):
    config_backup = get_config()
    scope_config = dataclasses.replace(config_backup)
    __set_config(scope_config)

    if retry_count is not None:
        scope_config.retry_count = retry_count

    if wait_after_fail is not None:
        scope_config.wait_after_fail = wait_after_fail

    try:
        yield
    finally:
        __set_config(config_backup)


def retry(action: Callable, on_fail: Consumer[Exception] = None):
    config = get_config()
    sequence = Sequence(retry_count=config.retry_count, wait_after_fail=config.wait_after_fail)
    exception: Optional[Exception] = None

    def _run():
        nonlocal exception
        try:
            action()
            exception = None
            return True
        except Exception as e:
            exception = e
            if on_fail:
                on_fail(e)

    sequence.run(_run)

    if exception is not None:
        raise RetryException(exception, sequence)
