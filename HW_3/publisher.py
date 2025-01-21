import json
import paho.mqtt.client as mqtt
import adafruit_dht
import uuid
from time import time, sleep
from datetime import datetime
from board import D4

mac_address = hex(uuid.getnode()) # Get the MAC address of the Raspberry PI
dht_device = adafruit_dht.DHT11(D4) # Declare the existence of the humidity-temperature sensor and indicate the linking pin! (D4)

# Create a new MQTT client
client = mqtt.Client()
# Connect to the MQTT broker
client.connect('mqtt.eclipseprojects.io', 1883)

mins = 15
secs = 0
end_time = time() + 60*mins + secs
while time() < end_time:
    timestamp = time()
    timestamp_ms = int(timestamp*1000)
    formatted_time = datetime.fromtimestamp(timestamp_ms/1000).strftime('%Y-%m-%d %H:%M:%S.%f') # Convert the timestamp to human-readable time

    try:
        # Get temperature and humidity from the sensor, store them in the database and print them
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        temp_hum_dict = {
            'mac_address': str(mac_address),
            'timestamp': timestamp,
            'temperature': temperature,
            'humidity': humidity,
        }

        temp_hum_string = json.dumps(temp_hum_dict)

        client.publish('s345139', temp_hum_string)

        print(f'{formatted_time} - {mac_address}:temperature = {temperature}')
        print(f'{formatted_time} - {mac_address}:humidity = {humidity}')
    except:
        # If the connection fails, print an error message and try to restart the connection
        # This is done because the connection is generally unrealiable
        print('Sensor failure')
        dht_device.exit()
        dht_device = adafruit_dht.DHT11(D4)

    sleep(2) # Check the temperature and humidity every 2 seconds