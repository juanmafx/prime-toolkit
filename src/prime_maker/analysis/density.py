from math import log
from typing import Final

EULER_MASCHERONI: Final = 0.5772156649015329


def logarithmic_integral(value: float) -> float:
    if value <= 1:
        raise ValueError("value must be greater than 1")
    log_value = log(value)
    total = EULER_MASCHERONI + log(log_value)
    power_term = 1.0
    index = 1
    while True:
        power_term *= log_value / index
        addend = power_term / index
        total += addend
        if index > log_value and abs(addend) < 1e-17 * abs(total):
            return total
        index += 1
