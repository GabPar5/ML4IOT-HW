import redis
from time import time, sleep
import uuid
from datetime import datetime
import adafruit_dht
from board import D4
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-h", "--host", default = None, type = str, help="Redis Cloud Host")
parser.add_argument("-p", "--port", default = None, type = int, help="Redis Cloud Port")
parser.add_argument("-u", "--user", default = None, type = str, help="Redis Cloud Username")
parser.add_argument("-p", "--password", default = None, type = str, help="Redis Cloud Password")

params = parser.parse_args()

# Implementation of LOSSLESS and LOSSY compression methods
mac_address = hex(uuid.getnode()) # Get the MAC address of the Raspberry PI
dht_device = adafruit_dht.DHT11(D4) # Declare the existence of the humidity-temperature sensor and indicate the linking pin! (D4)


# Database parameters
REDIS_HOST = params.host
REDIS_PORT = params.port
REDIS_USERNAME = params.user
REDIS_PASSWORD = params.password

# Establish a connection to the database and check if the connection works
redis_client = redis.Redis(host = REDIS_HOST, 
                           port = REDIS_PORT, 
                           username = REDIS_USERNAME, 
                           password = REDIS_PASSWORD) 

is_connected = redis_client.ping()
print('Connect:', is_connected)

# Create new time series for temperature and humidity
try:
    redis_client.ts().create(str(mac_address)+':temperature')
except:
    pass
try:
    redis_client.ts().create(str(mac_address)+':humidity')
except:
    pass

# Set the retention of the 'temperature' and 'humidity' time series to 30 days
one_day_in_ms = 24*60*60*1000
redis_client.ts().alter(mac_address + ':temperature', retention_msecs = one_day_in_ms*30)
redis_client.ts().alter(mac_address + ':humidity', retention_msecs = one_day_in_ms*30)


while True: # Record the temperature and humidity every 2 seconds until the key 'q' is pressed
    key = input()
    if key in ['q','Q']: # Disable recording of audio if the key 'q' is pressed
            print('Recording stopped')
            break
    timestamp_ms = int(time()*1000)
    formatted_time = datetime.fromtimestamp(timestamp_ms/1000).strftime('%Y-%m-%d %H:%M:%S.%f') # Convert the timestamp to human-readable time

    try:
        # Get temperature and humidity from the sensor, store them in the database and print them
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        redis_client.ts().add(str(mac_address)+':temperature', timestamp_ms, temperature)
        redis_client.ts().add(str(mac_address)+':humidity', timestamp_ms, humidity)

        print(f'{formatted_time} - {mac_address}:temperature = {temperature}')
        print(f'{formatted_time} - {mac_address}:humidity = {humidity}')
    except:
        # If the connection fails, print an error message and try to restart the connection
        # This is done because the connection is generally unrealiable
        print('Sensor failure - restarting now')
        dht_device.exit()
        dht_device = adafruit_dht.DHT11(D4)

    sleep(2) # Check the temperature and humidity every 2 seconds



# Create aggregated time series for temperature and humidity
# avg
try:
    redis_client.ts().create(mac_address + ':temperature_avg')
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_avg', 'avg', bucket_size_msec=1000*60*60)
    redis_client.ts().alter(mac_address + ':temperature_avg', retention_msecs = one_day_in_ms*365)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_avg')
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_avg', 'avg', bucket_size_msec=1000*60*60)
    redis_client.ts().alter(mac_address + ':humidity_avg', retention_msecs = one_day_in_ms*365)
except redis.ResponseError:
    pass

# min
try:
    redis_client.ts().create(mac_address + ':temperature_min')
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_min', 'min', bucket_size_msec=1000*60*60)
    redis_client.ts().alter(mac_address + ':temperature_min', retention_msecs = one_day_in_ms*365)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_min')
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_min','min', bucket_size_msec=1000*60*60)
    redis_client.ts().alter(mac_address + ':humidity_min', retention_msecs = one_day_in_ms*365)
except redis.ResponseError:
    pass

# max
try:
    redis_client.ts().create(mac_address + ':temperature_max')
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_max', 'max', bucket_size_msec=1000*60*60)
    redis_client.ts().alter(mac_address + ':temperature_max', retention_msecs = one_day_in_ms*365)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_max')
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_max','max', bucket_size_msec=1000*60*60)
    redis_client.ts().alter(mac_address + ':humidity_max', retention_msecs = one_day_in_ms*365)
except redis.ResponseError:
    pass



