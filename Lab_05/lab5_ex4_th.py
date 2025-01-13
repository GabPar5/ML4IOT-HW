import adafruit_dht
import redis
import time
import uuid
from datetime import datetime
from board import D4


REDIS_HOST = 'redis-12335.c74.us-east-1-4.ec2.redns.redis-cloud.com'
REDIS_PORT = 12335
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'WAZqGdJLk3ZVC1nGmcYggucmetQKGbb1'


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD
)
is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

mac_address = hex(uuid.getnode())
dht_device = adafruit_dht.DHT11(D4)


while True:
    timestamp = time.time()
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        timestamp_ms = int(timestamp * 1000)

        redis_client.ts().add(f'{mac_address}:temperature', timestamp_ms, temperature)
        redis_client.ts().add(f'{mac_address}:humidity', timestamp_ms, humidity)
    except:
        print(f'sensor failure')
        dht_device.exit()
        dht_device = adafruit_dht.DHT11(D4)

    time.sleep(2)