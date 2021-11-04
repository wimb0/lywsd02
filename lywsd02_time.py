#!/usr/bin/python3

import time
from datetime import datetime
import struct
from bluepy import btle

# MAC address of LYWSD02
mac_addr = '3F:59:C8:81:XX:XX'


# UUIDs
uuid_time = 'ebe0ccb7-7a0a-4b0c-8a1a-6ff2997da3a6'
uuid_battery = 'EBE0CCC4-7A0A-4B0C-8A1A-6FF2997DA3A6'

# Get offset in hours from GMT
utc_offset = time.localtime().tm_gmtoff
local_offset = int(utc_offset//3600)

# connect to device
try:
    print('Connecting to {0}'.format(mac_addr))
    p = btle.Peripheral (mac_addr)
except Exception as e:
    print('Error: {0}'.format(e))
    exit()

chtime = p.getCharacteristics (uuid = uuid_time)[0]

# read time and offset from device
value = chtime.read()
device_ts, device_offset = struct.unpack('Ib', value)
print('Current Time/Offset: {:%H:%M} / {}'.format(datetime.utcfromtimestamp(device_ts), device_offset))

try:
    # Get current epoch timestamp
    ts = int(round(time.time()))

    # Create array with bitmask (or shifted?) time parts
    # Idea from: https://github.com/Freeyourgadget/Gadgetbridge/blob/master/app/src/main/java/nodomain/freeyourgadget/gadgetbridge/service/devices/mijia_lywsd02/MijiaLywsd02Support.java
    arr_time_bytes = [(ts & 0xFF), ((ts>>8) & 0xFF),((ts>>16) & 0xFF),((ts>>24) & 0xFF),local_offset]


    # Send time to device
    print('Sending time and offset...'.format(mac_addr))
    chtime.write(bytearray(arr_time_bytes), withResponse = True)

finally:
    # read new time from device
    value = chtime.read()
    device_ts, device_offset = struct.unpack('Ib', value)
    print('New Time/Offset: {:%H:%M} / {}'.format(datetime.utcfromtimestamp(device_ts), device_offset))

    # get battery percentage from device
    chbatt = p.getCharacteristics(uuid=uuid_battery)[0]
    value = chbatt.read()
    print('Battery: {0}%'.format(ord(value)))

    # disconnect
    print('Done! Disconnecting from {0}'.format(mac_addr))
    p.disconnect()
