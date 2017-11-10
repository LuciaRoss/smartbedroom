#!/usr/bin/env python
import sys
from temperusb import temper
from time import time
from datetime import datetime, date
from pyHS100 import smartplug
import sqlite3
radiator = None

try:
    radiator = smartplug.SmartPlug("192.168.86.17")
except:
    pass

if radiator:
    on_data = radiator.state
else:
    on_data = "ERROR"

temp = temper.TemperHandler().get_devices()[0].get_temperature()

conn = None
try:
    conn = sqlite3.connect('../assistant/housecode.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS log (id int, date text, temp real, status text)''')
    t = time()
    cur.execute('''INSERT INTO log VALUES (?, ?, ?, ?)''', (t, datetime.fromtimestamp(t).strftime("%Y-%m-%d"), temp, on_data))
    conn.commit()
    conn.close()
except:
    print sys.exc_info()[0]
    pass



