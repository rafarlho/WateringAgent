# soil_sensor.py

from machine import ADC, Pin
import time

_VAL_DRY   = 336
_VAL_MOIST = 37321
_PIN       = 26


_sensor = ADC(Pin(_PIN))

def read_level() -> int:

    raw = _sensor.read_u16()
    pct = (raw - _VAL_DRY) / (_VAL_MOIST - _VAL_DRY) * 100
    return max(0, min(100, round(pct)))

if __name__ == "__main__":
    value = read_level()
    print(value , "%")