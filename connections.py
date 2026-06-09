# connections.py

import network
import ujson
import time
from umqtt.simple import MQTTClient

def connect_to_wifi(timeout_seconds=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(config.get("WIFI_SSID"),config.get("WIFI_PASS"))
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > timeout_seconds:
                print("Wifi connection timed out")
                return False
            time.sleep(0.5)
    print("Connected! Picos IP:", wlan.ifconfig()[0])

def load_env(filename="env.txt"):
    env_vars = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                
                if line.strip() and not line.strip().startswith("#"):
                    try:
                        key, value = line.strip().split("=", 1)
                        env_vars[key] = value
                    except ValueError:
                        pass 
    except OSError:
        print(f"Error: Could not find {filename}")
    return env_vars


config = load_env("env.txt")

def connect_to_mqtt():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("No wifi, cannot use MQTT")
        return None

    try:
        client = MQTTClient(
            config.get("CLIENT_ID"), 
            config.get("MQTT_BROKER"), 
            keepalive=60
        )
        
        
        client.connect()
        return client
    except Exception as e:
        return None

if __name__ == "__main__":
    
    ssid = config.get("WIFI_SSID")
    password = config.get("WIFI_PASS")
    print(ssid)
    connect_to_wifi()
    client = connect_to_mqtt()
    client.publish("watering_data", f"From {config.get("CLIENT_ID")} says hello!")