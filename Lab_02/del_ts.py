import redis
from datetime import datetime, timedelta

# WARNING: THIS NOTEBOOK DELETES EITHER ALL THE TIME SERIES OR THEIR VALUES STORED IN A DESIRED RANGE OF TIME

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

from_str = '2024-10-01 00:00:00'
to_str = '2024-10-22 20:00:00'

dt = timedelta(hours=2)

from_datetime = datetime.fromisoformat(from_str)
from_datetime_utc = from_datetime - dt
from_timestamp = from_datetime_utc.timestamp()
from_timestamp_ms = int(from_timestamp * 1000)

to_datetime = datetime.fromisoformat(to_str)
to_datetime_utc = to_datetime - dt
to_timestamp = to_datetime_utc.timestamp()
to_timestamp_ms = int(to_timestamp * 1000)

del_vals_only = False
if del_vals_only:
    redis_client.ts().delete(mac_address + ':temperature', from_timestamp_ms, to_timestamp_ms)
    redis_client.ts().delete(mac_address + ':humidity', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':temperature_avg', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':humidity_avg', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':temperature_min', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':humidity_min', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':temperature_max', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':humidity_max', from_timestamp_ms, to_timestamp_ms)
    redis_client.ts().delete(mac_address + ':temperature_uncompressed', from_timestamp_ms, to_timestamp_ms)
    redis_client.ts().delete(mac_address + ':humidity_uncompressed', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':temperature_avg_uncompressed', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':humidity_avg_uncompressed', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':temperature_min_uncompressed', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':humidity_min_uncompressed', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':temperature_max_uncompressed', from_timestamp_ms, to_timestamp_ms)
    redis_client.delete(mac_address + ':humidity_max_uncompressed', from_timestamp_ms, to_timestamp_ms)
    print('Deleted all chosen values!')
else:
    redis_client.delete(mac_address + ':temperature')
    redis_client.delete(mac_address + ':humidity')
    redis_client.delete(mac_address + ':temperature_avg')
    redis_client.delete(mac_address + ':humidity_avg')
    redis_client.delete(mac_address + ':temperature_min')
    redis_client.delete(mac_address + ':humidity_min')
    redis_client.delete(mac_address + ':temperature_max')
    redis_client.delete(mac_address + ':humidity_max')
    redis_client.delete(mac_address + ':temperature_uncompressed')
    redis_client.delete(mac_address + ':humidity_uncompressed')
    redis_client.delete(mac_address + ':temperature_avg_uncompressed')
    redis_client.delete(mac_address + ':humidity_avg_uncompressed')
    redis_client.delete(mac_address + ':temperature_min_uncompressed')
    redis_client.delete(mac_address + ':humidity_min_uncompressed')
    redis_client.delete(mac_address + ':temperature_max_uncompressed')
    redis_client.delete(mac_address + ':humidity_max_uncompressed')
    print('Deleted all time series!')
