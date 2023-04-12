from dataclasses import dataclass


@dataclass()
class TestConfig:
    raise_exception: bool = False
    retry_count: int = 3
    wait_after_fail: float = 0.2
