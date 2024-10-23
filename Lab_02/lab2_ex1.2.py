import redis

# Implementation of LOSSY compression methods

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

# Set the retention of the 'temperature' time series (LAB 01) to 1 day
one_day_in_ms = 24*60*60*1000
redis_client.ts().alter('temperature', retention_msecs = one_day_in_ms)

# Another method is creating a time series which derives from an aggregation of the original one
# Here we create a time series that stores the average temperature every 0.1s
try:
    redis_client.ts().create('temperature_avg')
    redis_client.ts().createrule('temperature','temperature_avg', bucket_size_msec=1000)
except redis.ResponseError:
    pass