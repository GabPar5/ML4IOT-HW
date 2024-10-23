# In this exercise we will use the humidity-temperature sensor and store data from its measurements on the PI

import adafruit_dht
import uuid
from time import time, sleep
from datetime import datetime
from board import D4
import redis

mac_address = hex(uuid.getnode()) # Get the MAC address of the Raspberry PI
dht_device = adafruit_dht.DHT11(D4) # Declare the existence of the humidity-temperature sensor and indicate the linking pin! (D4)

# Database parameters
REDIS_HOST = 'redis-16137.c85.us-east-1-2.ec2.redns.redis-cloud.com'
REDIS_PORT = '16137'
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'hiXoD1azaPf7SjA3k2HCveUX2G0lMjgr'

# Establish a connection to the database and check if the connection works
redis_client = redis.Redis(host = REDIS_HOST, 
                           port = REDIS_PORT, 
                           username = REDIS_USERNAME, 
                           password = REDIS_PASSWORD) 

is_connected = redis_client.ping()
print('Connect:', is_connected)

# Create new time series for temperature and humidity, if they don't exist
try:
    redis_client.ts.create(str(mac_address)+':temperature')
except:
    pass
try:
    redis_client.ts.create(str(mac_address)+':humidity')
except:
    pass
try:
    redis_client.ts.create(str(mac_address)+':temperature_uncompressed', uncompressed = True)
except:
    pass
try:
    redis_client.ts.create(str(mac_address)+':humidity_uncompressed', uncompressed = True)
except:
    pass

while True:
    timestamp_ms = int(time()*1000)
    formatted_time = datetime.fromtimestamp(timestamp_ms/1000).strftime('%Y-%m-%d %H:%M:%S.%f') # Convert the timestamp to human-readable time

    try:
        # Get temperature and humidity from the sensor, store them in the database and print them
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        redis_client.ts().add(str(mac_address)+':temperature', timestamp_ms, temperature)
        redis_client.ts().add(str(mac_address)+':humidity', timestamp_ms, humidity)
        redis_client.ts().add(str(mac_address)+':temperature_uncompressed', timestamp_ms, temperature)
        redis_client.ts().add(str(mac_address)+':humidity_uncompressed', timestamp_ms, humidity)

        print(f'{formatted_time} - {mac_address}:temperature = {temperature}')
        print(f'{formatted_time} - {mac_address}:humidity = {humidity}')
    except:
        # If the connection fails, print an error message and try to restart the connection
        # This is done because the connection is generally unrealiable
        print('Sensor failure NOOOOOOO :(((((')
        dht_device.exit()
        dht_device = adafruit_dht.DHT11(D4)

    sleep(2) # Check the temperature and humidity every 2 seconds