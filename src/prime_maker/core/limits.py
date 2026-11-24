from typing import Final

MAX_INPUT_BITS: Final = 4096
MAX_SIEVE_LIMIT: Final = 10**10
MAX_RANGE_HIGH: Final = 10**15
MAX_RANGE_SPAN: Final = 10**9
MAX_COUNT_LIMIT: Final = 10**13
MAX_ROUNDS: Final = 256
DEFAULT_ROUNDS: Final = 40


def require_bounded(name: str, value: int, minimum: int, maximum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
