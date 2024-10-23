import redis

# Implementation of LOSSLESS and LOSSY compression methods

# Mac Address of RPI
mac_address = '0xe45f01e89914'

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

# 2.1.a
# Create new time series for temperature and humidity, if they don't exist
try:
    redis_client.ts().create(str(mac_address)+':temperature_1')
except:
    pass
try:
    redis_client.ts().create(str(mac_address)+':humidity_1')
except:
    pass
try:
    redis_client.ts().create(str(mac_address)+':temperature_1_uncompressed', uncompressed = True)
except:
    pass
try:
    redis_client.ts().create(str(mac_address)+':humidity_1_uncompressed', uncompressed = True)
except:
    pass

# Set the retention of the 'temperature' and 'humidity' time series (LAB 01) to 1 day
one_day_in_ms = 24*60*60*1000
redis_client.ts().alter(mac_address + ':temperature_1', retention_msecs = one_day_in_ms)
redis_client.ts().alter(mac_address + ':humidity_1', retention_msecs = one_day_in_ms)
redis_client.ts().alter(mac_address + ':temperature_1_uncompressed', retention_msecs = one_day_in_ms)
redis_client.ts().alter(mac_address + ':humidity_1_uncompressed', retention_msecs = one_day_in_ms)

# 2.1.b
# Create aggregated time series (lossy compression method)
try:
    redis_client.ts().create(mac_address + ':temperature_avg', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':temperature_1',mac_address + ':temperature_avg', 'avg', bucket_size_msec=1000*30)
    redis_client.ts().alter(mac_address + ':temperature_avg', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_avg', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':humidity_1',mac_address + ':humidity_avg', 'avg', bucket_size_msec=1000*30)
    redis_client.ts().alter(mac_address + ':humidity_avg', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

# 2.1.c
try:
    redis_client.ts().create(mac_address + ':temperature_min', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':temperature_1',mac_address + ':temperature_min', 'min', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':temperature_min', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_min', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':humidity_1',mac_address + ':humidity_min','min', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':humidity_min', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

# 2.1.d
try:
    redis_client.ts().create(mac_address + ':temperature_max', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':temperature_1',mac_address + ':temperature_max', 'max', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':temperature_max', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_max', chunk_size=128)
    redis_client.ts().createrule(mac_address + ':humidity_1',mac_address + ':humidity_max','max', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':humidity_max', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass


# 2.1.e
print('------ COMPRESSED TIME SERIES STATISTICS ------')

print('Temperature memory usage:', redis_client.ts().info(mac_address + ':temperature_1').memory_usage, 'bytes')
print('Temperature total samples:', redis_client.ts().info(mac_address + ':temperature_1').total_samples)
print('Humidity memory usage:', redis_client.ts().info(mac_address + ':humidity_1').memory_usage, 'bytes')
print('Humidity total samples:', redis_client.ts().info(mac_address + ':humidity_1').total_samples)

print('Temperature (avg) memory usage:', redis_client.ts().info(mac_address + ':temperature_avg').memory_usage, 'bytes')
print('Temperature (avg) total samples:', redis_client.ts().info(mac_address + ':temperature_avg').total_samples)
print('Humidity (avg) memory usage:', redis_client.ts().info(mac_address + ':humidity_avg').memory_usage, 'bytes')
print('Humidity (avg) total samples:', redis_client.ts().info(mac_address + ':humidity_avg').total_samples)

print('Temperature (min) memory usage:', redis_client.ts().info(mac_address + ':temperature_min').memory_usage, 'bytes')
print('Temperature (min) total samples:', redis_client.ts().info(mac_address + ':temperature_min').total_samples)
print('Humidity (min) memory usage:', redis_client.ts().info(mac_address + ':humidity_min').memory_usage, 'bytes')
print('Humidity (min) total samples:', redis_client.ts().info(mac_address + ':humidity_min').total_samples)

print('Temperature (max) memory usage:', redis_client.ts().info(mac_address + ':temperature_max').memory_usage, 'bytes')
print('Temperature (max) total samples:', redis_client.ts().info(mac_address + ':temperature_max').total_samples)
print('Humidity (max) memory usage:', redis_client.ts().info(mac_address + ':humidity_max').memory_usage, 'bytes')
print('Humidity (max) total samples:', redis_client.ts().info(mac_address + ':humidity_max').total_samples)

# 2.1.f
try:
    redis_client.ts().create(mac_address + ':temperature_avg_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':temperature_1_uncompressed',mac_address + ':temperature_avg_uncompressed', 'avg', bucket_size_msec=1000*30)
    redis_client.ts().alter(mac_address + ':temperature_avg_uncompressed', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_avg_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':humidity_1_uncompressed',mac_address + ':humidity_avg_uncompressed', 'avg', bucket_size_msec=1000*30)
    redis_client.ts().alter(mac_address + ':humidity_avg_uncompressed', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':temperature_min_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':temperature_1_uncompressed',mac_address + ':temperature_min_uncompressed', 'min', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':temperature_min_uncompressed', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_min_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':humidity_1_uncompressed',mac_address + ':humidity_min_uncompressed','min', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':humidity_min_uncompressed', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':temperature_max_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':temperature_1_uncompressed',mac_address + ':temperature_max_uncompressed', 'max', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':temperature_max_uncompressed', retention_msecs = one_day_in_ms*30)

except redis.ResponseError:
    pass

try:
    redis_client.ts().create(mac_address + ':humidity_max_uncompressed', chunk_size=128, uncompressed = True)
    redis_client.ts().createrule(mac_address + ':humidity_1_uncompressed',mac_address + ':humidity_max_uncompressed','max', bucket_size_msec=1000*60)
    redis_client.ts().alter(mac_address + ':humidity_max_uncompressed', retention_msecs = one_day_in_ms*30)
except redis.ResponseError:
    pass

print('------ UNCOMPRESSED TIME SERIES STATISTICS ------')

print('Temperature memory usage (uncompressed):', redis_client.ts().info(mac_address + ':temperature_1_uncompressed').memory_usage, 'bytes')
print('Temperature total samples (uncompressed):', redis_client.ts().info(mac_address + ':temperature_1_uncompressed').total_samples)
print('Humidity memory usage (uncompressed):', redis_client.ts().info(mac_address + ':humidity_1_uncompressed').memory_usage, 'bytes')
print('Humidity total samples (uncompressed):', redis_client.ts().info(mac_address + ':humidity_1_uncompressed').total_samples)

print('Temperature (avg) memory usage (uncompressed):', redis_client.ts().info(mac_address + ':temperature_avg_uncompressed').memory_usage, 'bytes')
print('Temperature (avg) total samples (uncompressed):', redis_client.ts().info(mac_address + ':temperature_avg_uncompressed').total_samples)
print('Humidity (avg) memory usage (uncompressed):', redis_client.ts().info(mac_address + ':humidity_avg_uncompressed').memory_usage, 'bytes')
print('Humidity (avg) total samples (uncompressed):', redis_client.ts().info(mac_address + ':humidity_avg_uncompressed').total_samples)

print('Temperature (min) memory usage (uncompressed):', redis_client.ts().info(mac_address + ':temperature_min_uncompressed').memory_usage, 'bytes')
print('Temperature (min) total samples (uncompressed):', redis_client.ts().info(mac_address + ':temperature_min_uncompressed').total_samples)
print('Humidity (min) memory usage (uncompressed):', redis_client.ts().info(mac_address + ':humidity_min_uncompressed').memory_usage, 'bytes')
print('Humidity (min) total samples (uncompressed):', redis_client.ts().info(mac_address + ':humidity_min_uncompressed').total_samples)

print('Temperature (max) memory usage (uncompressed):', redis_client.ts().info(mac_address + ':temperature_max_uncompressed').memory_usage, 'bytes')
print('Temperature (max) total samples (uncompressed):', redis_client.ts().info(mac_address + ':temperature_max_uncompressed').total_samples)
print('Humidity (max) memory usage (uncompressed):', redis_client.ts().info(mac_address + ':humidity_max_uncompressed').memory_usage, 'bytes')
print('Humidity (max) total samples (uncompressed):', redis_client.ts().info(mac_address + ':humidity_max_uncompressed').total_samples)
