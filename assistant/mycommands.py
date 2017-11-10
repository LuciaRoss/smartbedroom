import sys
from hue import group, scene, bulb
from pyHS100.smartplug import SmartPlug
from datetime import datetime, date, timedelta
from dateutil.relativedelta import *
from dateutil import parser
from time import time
import json
import sqlite3

DB = 'housecode.db'
radiator = SmartPlug("192.168.86.17")

bedroom = group.Group("bed")
stairs = group.Group("stairs")

weekdays = {'monday':0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
months = ['january', 'february', 'marcj', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
class Vacation:
    def __init__(self, day, mode, heaterdate):
        self.mode = mode
        self.date = day
        self.hdate = heaterdate
    def jsonFormat(self):
        data = {}
        data['mode'] = self.mode
        data['date'] = self.day.strftime("%Y-%m-%d %H:%M:%S") if self.mode else None
        data['hdate'] = self.hdate.strftime("%Y-%m-%d %H:%M:%S") if self.mode else None
        return data
    def sqlFormat(self):
        i = int(time())
        m = str(self.mode)
        d = self.day.strftime("%Y-%m-%d %H:%M:%S") if self.mode else 'None'
        h = self.hdate.strftime("%Y-%m-%d %H:%M:%S") if self.mode else 'None'
        return (i, m, d, h)

vacation = Vacation(None, False, None)

commandList = []
sceneCommandDict = {}

class Command:
    def __init__(self,fun,triggerlist):
        self.triggers = [t.strip().lower() for t in triggerlist]
        self.fun = fun

    def run(self, extra = None):
        try:
            self.fun(extra)
        except Exception as e:
            print(e)

def heaton(extra):
    if "on" in extra:
        radiator.turn_on()
    else:
        radiator.turn_off()
commandList.append(Command(heaton,["turn the heat"]))

def lumosMaxima(extra):
    bedroom.maxima()
commandList.append(Command(lumosMaxima,["lumos maxima"]))

def lightsout(extra):
    bedroom.off()
    stairs.off()
commandList.append(Command(lightsout,["lights out", "turn the lights off","lights off"]))

def lightson(extra):
    bedroom.on()
    stairs.off()
commandList.append(Command(lightson,["lights on", "turn the lights on","light on"]))

def nightlight(extra):
    bedroom.nightlight()
commandList.append(Command(nightlight,["nightlight","night light","nightlife","night life"]))

def setScene(extra):
    bedroom.set_scene(extra.strip().lower())
commandList.append(Command(setScene,["set scene"]))

def dim(extra):
    bedroom.dim(45)
commandList.append(Command(dim,["dim the lights","less bright","not as bright","less light"]))

def brighter(extra):
    bedroom.brighter(45)
commandList.append(Command(brighter,["brighter","more light"]))

def warmer(extra):
    bedroom.warmer(70)
commandList.append(Command(warmer, ["warmer"]))

def colder(extra):
    bedroom.colder(70)
commandList.append(Command(warmer, ["colder"]))

def setBrightness(extra):
    bedroom.set_brightness((int(extra)*254)/100)
commandList.append(Command(setBrightness,["set brightness to"]))

def storeScene(extra):
    try:
        s = scene.Scene(extra)
        s.store()
    except:
        #create new scene
        scene.Scene.create(extra)
commandList.append(Command(storeScene, ["store"]))

def deleteScene(extra):
    s = scene.Scene(extra)
    s.delete()
commandList.append(Command(deleteScene, ["delete"]))

def modifyScene(extra):
    words = extra.split()
    s = scene.Scene(extra.split()[0])
    s.parseString(extra.split()[1:])
commandList.append(Command(modifyScene,["modify scene", "modify sing"]))

def vacationModeUntil(extra):
    current = date.today()
    words = extra.split()
    if 'next week' in extra:
        dt = current + relativedelta(weeks=+1)
    elif 'next month' in extra:
        dt = current + relativedelta(months=+1)
    elif 'next' in extra:
        dt = current + relativedelta(weekday=weekdays[words[1]])
    else:
        for w in words:
            if w[0].isdigit():
                day = w
            elif w.lower() in months:
                month = w
        tmp = parser.parse(day + " " + month)
        dt = parser.parse(day + " " + month + " " + str(current.year + 1)) if tmp.month < current.month  else parser.parse(day + " " + month + " " + str(current.year))

    vacation.mode = True
    vacation.day = dt
    vacation.hdate = dt + relativedelta(days=-1)
    executeQuery(DB, "INSERT INTO vacationmode VALUES (?, ?, ?, ?)", vacation.sqlFormat())

commandList.append(Command(vacationModeUntil, ["set vacation mode until"]))

def vacationModeFor(extra):
    current = date.today()
    words = extra.split()
    period = int(words[0])
    if words[1] == 'days':
        dt = current + relativedelta(days=+period)
    elif words[1] == 'weeks':
        dt = current + relativedelta(weeks=+period)
    elif words[1] == 'months':
        dt = current + relativedelta(months=+period)
    else:
        print("provided time is wrong")
        return
    vacation.mode = True
    vacation.day = dt
    vacation.hdate = dt + relativedelta(days=-1)
    executeQuery(DB, "INSERT INTO vacationmode VALUES (?, ?, ?, ?)", vacation.sqlFormat())
commandList.append(Command(vacationModeFor, ["set vacation mode for"]))

def exitVacationMode(extra):
    vacation.mode = False
    vacation.day = None
    vacation.hdate = None
    executeQuery(DB, "INSERT INTO vacationmode VALUES (?, ?, ?, ?)", vacation.sqlFormat())
commandList.append(Command(exitVacationMode, ["exit vacation mode"]))

def executeQuery(database, query, args):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute(query, args)
        conn.commit()
        conn.close()
    except:
        pass
def refreshScenes():
    global sceneCommandDict
    for s in scene.Scene.get_names():
        sceneCommandDict[s]= Command(setScene, [s])

refreshScenes()

commandDict = {trigger.lower():command for command in commandList for trigger in command.triggers}
