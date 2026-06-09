# pump_relay.py

from machine import Pin

_PIN = 15

_actor = Pin(_PIN, Pin.OUT, value=0)

def turn_on() -> void:
    _actor.value(1)
    
def turn_off() -> void:
    _actor.value(0)

if __name__ == "__main__":    
    print("Pump is off by default")

