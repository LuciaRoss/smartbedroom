#!/usr/bin/env python
import sys
import os
from temperusb import temper
from time import time
from pyHS100 import smartplug
from datetime import datetime
import json
import sqlite3

dir1 = '../assistant/hue'
dir2='../assistant'
sys.path.append(dir1)
sys.path.append(dir2)

import mycommands
import group

#check for errors
mode = False
hdate = None

class Temp:
    def __init__(self, l, u):
        self.upper = u
        self.lower = l

def isday(hour):
    return hour >= 7 and hour < 22

def isevening(hour):
    return hour >= 22 and hour < 23

def isnight(hour):
    return hour >= 23 or hour < 7

def lightson():
    return bedroom.ison()
def ison():
    return on_data == "ON"

bedroom = group.Group("bed")
stairs = group.Group("stairs")

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

try:
    conn = sqlite3.connect('../assistant/housecode.db')
    cur = conn.cursor()
    for row in cur.execute("SELECT mode, hdate FROM vacationmode ORDER BY id DESC LIMIT 1"):
        mode = True if row[0] == 'True' else False
        hdate = datetime.strptime(row[1], "") if mode else None

    cur.execute('''CREATE TABLE IF NOT EXISTS log (id int, date text, temp real, status text)''')
    t = time()
    cur.execute('''INSERT INTO log VALUES (?, ?, ?, ?)''', (t, datetime.fromtimestamp(t).      strftime("%Y-%m-%d"), temp, on_data))

except:
    print sys.exc_info()[0]
    pass

hour = datetime.now().hour
current = datetime.now().date()
vacation = Temp(15.0, 18.0)
normal = Temp(20, 21)
night = Temp(18.0, 19)

state = "NOTSET"
if on_data == 'ERROR':
    state = 'error'
elif mode:
    if current == hdate.date() and temp < vacation.lower and radiator.is_off:
        radiator.turn_on()
        state = "TURNED ON -> last day of vacation"
    elif current == hdate.date() and temp > vacation.upper and radiator.is_on:
        radiator.turn_off()
        state = "TURNED OFF -> last day of vacation"
elif temp >= normal.upper and radiator.is_on:
    radiator.turn_off()
    state = "TURNED OFF"
elif isday(hour) and lightson() and temp < normal.lower and radiator.is_off:
    radiator.turn_on()
    state = "TURNED ON -> DAY lights on"
elif isday(hour) and not lightson() and temp < night.upper and radiator.is_off:
    radiator.turn_on()
    state = "TURNED ON -> DAY lights off"
elif isday(hour) and not lightson() and temp >= normal.lower and radiator.is_on:
    radiator.turn_off()
    state = "TURNED OFF -> DAY lights off"
elif isnight(hour) and not lightson() and temp < night.lower and radiator.is_off:
    radiator.turn_on()
    state = "TURNED ON -> NIGHT lights off"
elif isnight(hour) and not lightson() and temp >= night.upper and radiator.is_on:
    radiator.turn_off()
    state = "TURNED OFF -> NIGHT lights off"
elif isnight(hour) and lightson() and temp < night.upper and radiator.is_off:
    radiator.turn_on()
    state = "TURNED ON -> NIGHT lights on"
elif isnight(hour) and lightson() and temp >= normal.lower and radiator.is_on:
    radiator.turn_off()
    state = "TURNED OFF -> NIGHT lights on"

if state != "NOT SET":
    cur.execute('''INSERT INTO heaterstatus VALUES (?, ?, ?, ?, ?, ?)''', (int(time()), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), temp, str(on_data), str(lightson()), state))

conn.commit()
conn.close()
