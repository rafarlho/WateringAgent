# temp_hum_sensor.py

from machine import Pin
import dht
import time

_PIN = 22

_sensor = dht.DHT22(Pin(_PIN))

def read_level() -> dict:
    try:
        _sensor.measure()
        temp = _sensor.temperature()
        hum = _sensor.humidity()
        return {"t": temp, "h": hum}
    except OSError as e:
        print("Error reading: ",e)
        return {"t": None, "h": None}

if __name__ == "__main__":
    
    value = read_level()
    print(value)
