import dataclasses
import logging
from dataclasses import dataclass
from time import sleep, time
from typing import Callable

import inject

from paf.common import Property
from paf.types import Consumer


@dataclass()
class Config:
    retry_count: int = Property.env(Property.PAF_SEQUENCE_RETRY_COUNT)
    wait_after_fail: float = Property.env(Property.PAF_SEQUENCE_WAIT_AFTER_FAIL)


class Sequence:
    def __init__(self, retry_count: int = 3, wait_after_fail: float = 0.2):
        self._max = retry_count
        self._wait = wait_after_fail
        self._count = 0
        self._start_time = 0

    def run(self, sequence: Callable[[], bool]):
        self._start_time = time()
        while True:
            if sequence() or self._count >= self._max:
                break

            self._count += 1
            sleep(self._wait)

    @property
    def duration(self):
        return time() - self._start_time

    @property
    def count(self):
        return self._count


class RetryException(Exception):
    def __init__(self, sequence: Sequence, *args, **kwargs):
        super().__init__(args, kwargs)
        self._sequence = sequence

    @property
    def sequence(self):
        return self._sequence


class Control:

    __global_config: Config = Config()

    def retry(
        self,
        action: Callable,
        on_fail: Consumer[Exception] = None,
        count: int = None,
        wait_after_fail: float = None
    ):
        config_backup = Control.__global_config
        config = dataclasses.replace(config_backup)
        Control.__global_config = config

        if count is not None:
            config.retry_count = count

        if wait_after_fail is not None:
            config.wait_after_fail = wait_after_fail

        sequence = Sequence(retry_count=config.retry_count, wait_after_fail=config.wait_after_fail)
        exception = None

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

        Control.__global_config = config_backup

        if exception:
            raise RetryException(sequence, f"{exception} after {sequence.count} retries ({round(sequence.duration, 2)} seconds)")


def inject_config(binder: inject.Binder):
    binder.bind(Control, Control())
