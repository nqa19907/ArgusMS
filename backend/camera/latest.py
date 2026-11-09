import threading
from typing import Generic, TypeVar

T = TypeVar("T")


class LatestValue(Generic[T]):
    def __init__(self) -> None:
        self._cond = threading.Condition()
        self._value: T | None = None
        self._seq: int = 0

    def replace(self, value: T) -> int:
        with self._cond:
            self._seq += 1
            self._value = value
            self._cond.notify_all()
            return self._seq

    def get(self) -> tuple[T | None, int]:
        with self._cond:
            return self._value, self._seq

    def wait_newer(self, last_seq: int, timeout: float = 0.5) -> tuple[T | None, int]:
        with self._cond:
            if self._seq <= last_seq:
                self._cond.wait(timeout=timeout)
            if self._seq > last_seq:
                return self._value, self._seq
            return None, self._seq

    def clear(self) -> None:
        with self._cond:
            self._value = None
            self._seq += 1
            self._cond.notify_all()