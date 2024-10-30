import redis
from time import time, sleep
from datetime import datetime
import uuid
import adafruit_dht
from board import D4
import argparse


# Parse arguments passed when running this script through the terminal
parser = argparse.ArgumentParser()
parser.add_argument("-ho", "--host", default = None, type = str, help="Redis Cloud Host")
parser.add_argument("-po", "--port", default = None, type = int, help="Redis Cloud Port")
parser.add_argument("-us", "--user", default = None, type = str, help="Redis Cloud Username")
parser.add_argument("-pw", "--password", default = None, type = str, help="Redis Cloud Password")
params = parser.parse_args()

# Parameters and constants
REDIS_HOST = params.host
REDIS_PORT = params.port
REDIS_USERNAME = params.user
REDIS_PASSWORD = params.password
ONE_DAY_IN_MS = 24*60*60*1000
RETENTION_DAYS = 30
RETENTION_DAYS_AGG = 365
SLEEP_SECS = 2
BUCKET_SIZE_MINS = 60

# Get the MAC address of the Raspberry PI and identify the humidity-temperature sensor
mac_address = hex(uuid.getnode()) 
dht_device = adafruit_dht.DHT11(D4)

# Establish a connection to the database and check if it works
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

# Set the retention of the 'temperature' and 'humidity' time series to "RETENTION_DAYS" days (in this case 30)
redis_client.ts().alter(mac_address + ':temperature', retention_msecs = ONE_DAY_IN_MS*RETENTION_DAYS)
redis_client.ts().alter(mac_address + ':humidity', retention_msecs = ONE_DAY_IN_MS*RETENTION_DAYS)

try: 
    # Record the temperature and humidity every "SLEEP_SECS" seconds (in this case 2) until the key "CTRL^C" is pressed
    while True: 
        
        # Get the timestamp in ms and convert it to human-readable time
        timestamp_ms = int(time()*1000)
        formatted_time = datetime.fromtimestamp(timestamp_ms/1000).strftime('%Y-%m-%d %H:%M:%S.%f')

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

        sleep(SLEEP_SECS)
except KeyboardInterrupt:
    pass


# Create aggregated time series for temperature and humidity,
# calculating them every "BUCKET_MINS" minutes (in this case 60).
# Set their retention period to "RETENTION_DAYS_AGG" days (in this case 365)
# avg
print(f"calculating metrics...")
try:
    redis_client.ts().create(mac_address + ':temperature_avg')
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_avg', 'avg', bucket_size_msec=1000*60*BUCKET_SIZE_MINS)
    redis_client.ts().alter(mac_address + ':temperature_avg', retention_msecs = ONE_DAY_IN_MS*RETENTION_DAYS_AGG)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_avg')
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_avg', 'avg', bucket_size_msec=1000*60*BUCKET_SIZE_MINS)
    redis_client.ts().alter(mac_address + ':humidity_avg', retention_msecs = ONE_DAY_IN_MS*RETENTION_DAYS_AGG)
except redis.ResponseError:
    pass

# min
try:
    redis_client.ts().create(mac_address + ':temperature_min')
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_min', 'min', bucket_size_msec=1000*60*BUCKET_SIZE_MINS)
    redis_client.ts().alter(mac_address + ':temperature_min', retention_msecs = ONE_DAY_IN_MS*RETENTION_DAYS_AGG)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_min')
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_min','min', bucket_size_msec=1000*60*BUCKET_SIZE_MINS)
    redis_client.ts().alter(mac_address + ':humidity_min', retention_msecs = ONE_DAY_IN_MS*RETENTION_DAYS_AGG)
except redis.ResponseError:
    pass

# max
try:
    redis_client.ts().create(mac_address + ':temperature_max')
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_max', 'max', bucket_size_msec=1000*60*BUCKET_SIZE_MINS)
    redis_client.ts().alter(mac_address + ':temperature_max', retention_msecs = ONE_DAY_IN_MS*RETENTION_DAYS_AGG)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_max')
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_max','max', bucket_size_msec=1000*60*BUCKET_SIZE_MINS)
    redis_client.ts().alter(mac_address + ':humidity_max', retention_msecs = ONE_DAY_IN_MS*RETENTION_DAYS_AGG)
except redis.ResponseError:
    pass



