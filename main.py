# main.py

from soil_sensor import read_level as read_soil_h
from temp_hum_sensor import read_level as read_t_h
from pump_relay import turn_on as pump_on, turn_off as pump_off
from connections import connect_to_wifi, connect_to_mqtt, config
import time
import json

pump_off()
connect_to_wifi()
client = connect_to_mqtt()

def ensure_connected(client):
    try:
        client.ping()
        return client
    except Exception:
        print("MQTT disconnected, reconnecting...")
        return connect_to_mqtt()
    
while True:
    try:
        client = ensure_connected(client)
        print("Starting polling cycle")
        soil_h = read_soil_h()
        air_data = read_t_h()
        
        # Needs watering
        if soil_h <= 40:
            payload = json.dumps({
                "origin":config.get("CLIENT_ID"),
                "type": "info",
                "soil_h" : read_soil_h(),
                "air_h" : air_data["h"],
                "air_t": air_data["t"],
                "was_watered": "watering_starting"
            })
            if client is not None:
                client.publish("watering_data",payload )
            
            time.sleep(1)
            print("Pumping...")
            pump_on()
            try: 
                time.sleep(20)
            finally:
                pump_off()
            print("Pumping finished")
            time.sleep(1)
            
            soil_h = read_soil_h()
            air_data = read_t_h()
            payload = json.dumps({
                "origin":config.get("CLIENT_ID"),
                "type": "info",
                "soil_h" : soil_h,
                "air_h" : air_data["h"],
                "air_t": air_data["t"],
                "was_watered": "watering_finished"
                })
            if client is not None:
                client.publish("watering_data",payload )
        # No watering needed
        else: 
            payload = json.dumps({
                "origin":config.get("CLIENT_ID"),
                "type": "info",
                "soil_h" : read_soil_h(),
                "air_h" : air_data["h"],
                "air_t": air_data["t"],
                "was_watered": "not_watered"
                })
            if client is not None:
                client.publish("watering_data",payload )
        print("Finished polling cycle")
        for _ in range(30):
            time.sleep(60)
            if client is not None:
                payload = json.dumps({
                    "origin": config.get("CLIENT_ID"),
                    "type": "keep_alive"
                })
                client.publish("watering_data", payload)
    except Exception as e:
        print(f"Error in polling cycle: {e}")
        time.sleep(5)

    
