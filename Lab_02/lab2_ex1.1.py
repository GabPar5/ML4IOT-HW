from time import time, sleep
import redis

# Implementation of LOSSLESS compression methods

# Database parameters
REDIS_HOST = 'redis-11437.c250.eu-central-1-1.ec2.redns.redis-cloud.com'
REDIS_PORT = '11437'
REDIS_USERNAME = 'default'
REDIS_PASSWORD = 'tr1oc2EvY67MMIVobjvtUaeDgN8Y1iZS'

# Establish a connection to the database and check if the connection works
redis_client = redis.Redis(host = REDIS_HOST, 
                           port = REDIS_PORT, 
                           username = REDIS_USERNAME, 
                           password = REDIS_PASSWORD) 

is_connected = redis_client.ping()
print('Connect:', is_connected)

# Create a new time series
try:
    redis_client.ts().create('temperature_new', chunk_size = 128)
except redis.ResponseError:
    pass

# Check the memory usage, total samples and chunk count of the newly created time series
print(redis_client.ts().info('temperature_new').memory_usage)
print(redis_client.ts().info('temperature_new').total_samples)
print(redis_client.ts().info('temperature_new').chunk_count)

# Add some toy data to the time series to check the memory usage 
for i in range(100):
    timestamp_ms = int(time()*1000)
    redis_client.ts().add('temperature_new', timestamp_ms, 25+i//50)
    sleep(0.1)

print(redis_client.ts().info('temperature_new').memory_usage)
print(redis_client.ts().info('temperature_new').total_samples)
print(redis_client.ts().info('temperature_new').chunk_count)


# Create an uncompressed time series to check differences
try:
    redis_client.ts().create('temperature_uncompressed', chunk_size = 128, uncompressed = True)
except redis.ResponseError:
    pass

# Add some toy data to the time series to check the memory usage 
for i in range(100):
    timestamp_ms = int(time()*1000)
    redis_client.ts().add('temperature_uncompressed', timestamp_ms, 25+i//50)
    sleep(0.1)

# Check the memory usage, total samples and chunk count of the uncompressed time series
print(redis_client.ts().info('temperature_uncompressed').memory_usage)
print(redis_client.ts().info('temperature_uncompressed').total_samples)
print(redis_client.ts().info('temperature_uncompressed').chunk_count)
