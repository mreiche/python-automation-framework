from time import sleep, time
from typing import Callable


class RetrySequence:
    def __init__(self, retry_count: int = 3, wait_ms: float = 0.2):
        self._max = retry_count
        self._wait_ms = wait_ms
        self._count = 0

    def run(self, sequence: Callable):
        start = time()
        while True:
            self._count += 1
            try:
                sequence()
                break
            except Exception as e:
                sleep(self._wait_ms)
                if self._count >= self._max:
                    end = time()
                    duration = end - start
                    raise Exception(f"Sequence failed after {self._max} retries ({round(duration, 2)} seconds): {repr(e)}")
