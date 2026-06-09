# WateringAgent - an automatic watering system

An embedded project built with a **Raspberry Pi Pico W** to automate the watering of strawberry plants based on real sensor readings, publishing all data to an external **MQTT broker**.

---

## Motivation

Watering strawberries sounds simple — until you forget twice in a row during a heatwave. That's exactly where this came from: not from a need to scale a farm, but from wanting to solve a real, concrete problem while learning more about embedded systems, MicroPython, and IoT communication in a project that actually does something useful.

Strawberries are particularly sensitive to soil moisture. Too little and the plant dries out; too much and the roots rot. It made sense to let a sensor make that call more precisely than any fixed timer ever could.

---

## Goal

Build an autonomous system that:

- Continuously reads **soil moisture** and **air temperature/humidity**
- Makes watering decisions based on real thresholds — not fixed schedules
- Publishes all events and sensor readings to an **MQTT broker** for remote monitoring
- Runs reliably and recovers gracefully from network interruptions

---

## Hardware

| Component | Role |
|---|---|
| Raspberry Pi Pico W | Main microcontroller with built-in Wi-Fi |
| Capacitive soil sensor YL-100 | Soil moisture reading (analog, GPIO 26) |
| DHT22 sensor (AM2302) | Air temperature and humidity (digital, GPIO 22) |
| Relay module | Controls the water pump (GPIO 15) |
| Mini submersible pump | Delivers water to the soil |

Everything is wired on a breadboard, with the sensors and relay powered directly from the Pico W.

![alt text](https://raw.githubusercontent.com/rafarlho/WateringAgent/refs/heads/main/layout.png "Title")

---

## Implementation

### Code structure

```
├── main.py              # Main control loop and decision logic
├── soil_sensor.py       # Soil sensor reading and normalisation
├── temp_hum_sensor.py   # DHT22 reading
├── pump_relay.py        # Relay/pump control
└── connections.py       # Wi-Fi, MQTT, and config loading
```

### Watering logic

The system checks soil moisture continuously. If the value drops below **40%**, the pump is activated for **20 seconds**. MQTT messages with full sensor readings are published both before and after each watering event.

When no watering is needed, the polling cycle repeats every **30 minutes**, with keep-alive messages sent every minute to keep the broker connection alive.

### Soil sensor calibration

The capacitive sensor returns raw 16-bit values that were calibrated empirically:

```python
_VAL_DRY   = 336     # sensor in open air
_VAL_MOIST = 37321   # sensor fully submerged in water
```

Readings are normalised to a 0–100% scale, making thresholds easy to reason about and adjust.

---

## MQTT Communication

All communication between the Pico W and the rest of the system goes through **MQTT**, a lightweight messaging protocol well suited for resource-constrained devices.

### Architecture

```
Raspberry Pi Pico W
        │
        │  Wi-Fi
        ▼
   MQTT Broker
  (e.g. Mosquitto)
        │
        ├──▶ Dashboard / Monitoring
        └──▶ Other subscribers
```

The Pico W acts as a **publisher** on the `watering_data` topic. Any MQTT client subscribed to that topic receives the data in real time.

### Message format

All messages are published as JSON and differentiated by the `type` field:

**Sensor reading (with or without watering):**
```json
{
  "origin": "pico_strawberry_1",
  "type": "info",
  "soil_h": 38,
  "air_h": 62.4,
  "air_t": 23.1,
  "was_watered": "watering_starting"
}
```

The `was_watered` field can take three values:
- `"not_watered"` — soil moisture is fine, no action taken
- `"watering_starting"` — watering has just begun (reading taken before)
- `"watering_finished"` — watering is complete (reading taken after)

**Keep-alive:**
```json
{
  "origin": "pico_strawberry_1",
  "type": "keep_alive"
}
```

### Connection resilience

Before every polling cycle, the system actively checks whether the MQTT connection is still alive via `ping()`. If it has dropped, it reconnects automatically without interrupting the control loop.

---

## Configuration

Credentials are loaded from an `env.txt` file stored at the root of the Pico W (not included in the repository):

```
WIFI_SSID=your_network_name
WIFI_PASS=your_password
MQTT_BROKER=your_broker_address
CLIENT_ID=pico_strawberry_1
```

---

