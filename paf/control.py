from dataclasses import dataclass
from time import sleep, time
from typing import Callable

import inject


@dataclass()
class Config:
    raise_exception: bool = True
    retry_count: int = 3
    wait_after_fail: float = 0.3


class Sequence:
    def __init__(self, retry_count: int = 3, wait_after_fail: float = 0.2):
        self._max = retry_count
        self._wait_ms = wait_after_fail
        self._count = 0
        self._start_time = 0

    def run(self, sequence: Callable[[], bool]):
        self._start_time = time()
        while True:
            if sequence() or self._count >= self._max:
                break

            self._count += 1
            sleep(self._wait_ms)

    @property
    def duration(self):
        return time() - self._start_time

    @property
    def count(self):
        return self._count


class Control:
    def retry(self, action: Callable, on_fail: Callable = None, config: Config = Config()):
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
                    on_fail()

        sequence.run(_run)
        if exception:
            raise Exception(f"{exception} after {sequence.count} retries ({round(sequence.duration, 2)} seconds)")


def inject_config(binder: inject.Binder):
    binder.bind(Control, Control())
