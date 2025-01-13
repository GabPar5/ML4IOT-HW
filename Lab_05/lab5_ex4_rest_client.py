"""
This example shows how to test the API with a Python Client.
"""

import requests


host = "https://799d8518-7eff-43b1-a4b1-4fa1ee546f02.deepnoteproject.com"

# Check the service status
response = requests.get(host + '/status')
if response.status_code == 200:
    # print(response.json())
    status = response.json()['status']
    print(f'The server is {status}.')
else:
    print('The server is offline.')
    exit()

# Add one sensor.
# First, define the request body.
# You can use a Python object.
# The "requests" package will handle the conversion to JSON internally.
payload = {'mac_address': '0xdca632c91d8d'}
# Specify the request body with "json" argument of the post method.
response = requests.post(host + '/sensors', json=payload)

# Check the response code. The expected value is 200.
if response.status_code == 200:
    print('Sensor timeseries added.')
else:
    print(response.status_code, response.reason)
    exit()

# Print the list of all sensors
response = requests.get(host + '/sensors')

if response.status_code == 200:
    print('All sensors timeseries:')
    data = response.json()
    sensors = data['sensors']
    for sensor in sensors:
        # print(response.json())
        mac_address = sensor['mac_address']
        t_samples = sensor['t_samples']
        t_retention = sensor['t_retention']
        h_samples = sensor['h_samples']
        h_retention = sensor['h_retention']
        print(f'{mac_address} - Temperature: Samples={t_samples}, Retention={t_retention}ms')
        print(f'{mac_address} - Humidity: Samples={h_samples}, Retention={h_retention}ms')
else:
    print(response.status_code, response.reason)
    exit()

# •	Print the list of sensors with more than 10 temperature records.
# First, define the request query parameters.
# You can use a Python object.
# The "requests" package will handle the conversion to query internally.
payload = {"min_t_samples": 10}
# Specify the request query parameters with the "params" argument of the get method.
response = requests.get(host + '/sensors', params=payload)

if response.status_code == 200:
    print()
    print('Sensors timeseries with more than 10 temperature samples:')
    data = response.json()
    sensors = data['sensors']
    for sensor in sensors:
        mac_address = sensor['mac_address']
        print(mac_address)
else:
    print(response.status_code, response.reason)
    exit()

# Modify the temperature retention period of the created sensor to 2 days.
mac_address = '0xdca632c91d8d'
payload = {
    't_retention': 172800000,
    'h_retention': 86400000
}
response = requests.put(host + f'/sensor/{mac_address}', json=payload)

if response.status_code == 200:
    print()
    print('Sensor timeseries updated.')
else:
    print(response.status_code, response.reason)
    exit()

# Delete the sensor timeseries
response = requests.delete(host + f'/sensor/{mac_address}')
if response.status_code == 200:
    print()
    print('Sensor timeseries deleted.')
else:
    print(response.status_code, response.reason)
    exit()