# In this notebook we will learn how to work with Redis database
# Then we will integrate it with the monitoring of temperature/humidity

import redis

REDIS_HOST = 'redis-16034.c135.eu-central-1-1.ec2.redns.redis-cloud.com'
REDIS_PORT = '16034'
# Username and Password are the ones of the database, not of the Redis account!
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'wcgcuwxMCtJZd9piadNXW0R8tQPIzIFZ'

redis_client = redis.Redis(host = REDIS_HOST, 
                           port = REDIS_PORT, 
                           username = REDIS_USERNAME, 
                           password = REDIS_PASSWORD) # Establish a connection to the database

is_connected = redis_client.ping() # Check if the connection still works
print('Connect:', is_connected)


written = redis_client.set("message", "Welcome to Redis") # Create a new record (key, value)
print('written:', written) # Check if the record was written successfully

msg = redis_client.get("message") # Retrieve a record using its key and print it
print(msg.decode())

# The records stored in the redis database can be viewed (and written) from ANY device, including deepnote!