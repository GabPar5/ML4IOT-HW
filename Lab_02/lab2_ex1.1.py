from time import time, sleep
import redis

# Implementation of LOSSLESS and LOSSY compression methods

# Mac Address of RPI
mac_address = '0xe45f01e89914'

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

# 2.a
# Set the retention of the 'temperature' and 'humidity' time series (LAB 01) to 1 day
one_day_in_ms = 24*60*60*1000
redis_client.ts().alter(mac_address + ':temperature', retention_msecs = one_day_in_ms)
redis_client.ts().alter(mac_address + ':humidity', retention_msecs = one_day_in_ms)
redis_client.ts().alter(mac_address + ':temperature_uncompressed', retention_msecs = one_day_in_ms)
redis_client.ts().alter(mac_address + ':humidity_uncompressed', retention_msecs = one_day_in_ms)

# 2.b
# Create aggregated time series (lossy compression method)
try:
    redis_client.ts().create(mac_address + ':temperature_avg', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_avg', 'avg', bucket_size_msec=1000*30)
    redis_client.ts().alter(mac_address + ':temperature_avg', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_avg', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_avg', 'avg', bucket_size_msec=1000*30)
    redis_client.ts().alter(mac_address + ':humidity_avg', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

# 2.c
try:
    redis_client.ts().create(mac_address + ':temperature_min', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_min', 'min', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':temperature_min', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_min', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_min','min', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':humidity_min', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

# 2.d
try:
    redis_client.ts().create(mac_address + ':temperature_max', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':temperature',mac_address + ':temperature_max', 'max', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':temperature_max', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_max', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':humidity',mac_address + ':humidity_max','max', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':humidity_max', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass


# 2.e
print(redis_client.ts().info('temperature').memory_usage)
print(redis_client.ts().info('temperature').total_samples)
print(redis_client.ts().info('humidity').memory_usage)
print(redis_client.ts().info('humidity').total_samples)

print(redis_client.ts().info('temperature_avg').memory_usage)
print(redis_client.ts().info('temperature_avg').total_samples)
print(redis_client.ts().info('humidity_avg').memory_usage)
print(redis_client.ts().info('humidity_avg').total_samples)

print(redis_client.ts().info('temperature_min').memory_usage)
print(redis_client.ts().info('temperature_min').total_samples)
print(redis_client.ts().info('humidity_min').memory_usage)
print(redis_client.ts().info('humidity_min').total_samples)

print(redis_client.ts().info('temperature_max').memory_usage)
print(redis_client.ts().info('temperature_max').total_samples)
print(redis_client.ts().info('humidity_max').memory_usage)
print(redis_client.ts().info('humidity_max').total_samples)

# 2.f
try:
    redis_client.ts().create(mac_address + ':temperature_avg_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':temperature_uncompressed',mac_address + ':temperature_avg_uncompressed', 'avg', bucket_size_msec=1000*30)
    redis_client.ts().alter(mac_address + ':temperature_avg_uncompressed', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_avg_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':humidity_uncompressed',mac_address + ':humidity_avg_uncompressed', 'avg', bucket_size_msec=1000*30)
    redis_client.ts().alter(mac_address + ':humidity_avg_uncompressed', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':temperature_min_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':temperature_uncompressed',mac_address + ':temperature_min_uncompressed', 'min', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':temperature_min_uncompressed', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_min_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':humidity_uncompressed',mac_address + ':humidity_min_uncompressed','min', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':humidity_min_uncompressed', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':temperature_max_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':temperature_uncompressed',mac_address + ':temperature_max_uncompressed', 'max', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':temperature_max_uncompressed', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_max_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':humidity_uncompressed',mac_address + ':humidity_max_uncompressed','max', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':humidity_max_uncompressed', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass