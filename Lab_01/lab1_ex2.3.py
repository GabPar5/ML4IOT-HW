# In this notebook we will learn how to create and store a time series on Redis

import redis
from time import time

REDIS_HOST = 'redis-16034.c135.eu-central-1-1.ec2.redns.redis-cloud.com'
REDIS_PORT = '16034'
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'wcgcuwxMCtJZd9piadNXW0R8tQPIzIFZ'

redis_client = redis.Redis(host = REDIS_HOST, 
                           port = REDIS_PORT, 
                           username = REDIS_USERNAME, 
                           password = REDIS_PASSWORD) # Establish a connection to the database

is_connected = redis_client.ping() # Check if the connection still works
print('Connect:', is_connected)

try:
    redis_client.ts.create('integers') # Create a new time series, if it doesn't exist
except:
    pass # If the time series already exists, go on

timestamp_ms = int(time() * 1000)

redis_client.ts().add('integers', timestamp_ms, 1) # Add a record to the time series

# This code can be adapted so that it reads the temperature and humidity from the raspberry PI