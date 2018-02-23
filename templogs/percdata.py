from dateutil.relativedelta import *
from dateutil import parser
from time import time
from datetime import datetime, date
import sqlite3

class PercData:
    def __init__(self, period = None):
        self.raw_data = {}
        startdate = (date.today() + relativedelta(days=-period)).strftime("%Y-%m-%d") if period is not None else '1970-01-01'
        conn = sqlite3.connect('../assistant/housecode.db')
        cur = conn.cursor()
        for row in cur.execute('''select * from heatpercentage where date >= ?''', (startdate, )):
            self.raw_data[parser.parse(row[0])] = row[1]
        self.raw_data = sorted(self.raw_data.items())
        conn.close()
        self.calculate()
    def calculate(self):
        self.yesterday = int(self.raw_data[-1:][0][1])
        self.lastWeek = int(sum([x[1] for x in self.raw_data[-7:]])/7 if len(self.raw_data)>=7 else -1)
        self.lastmonth= int(sum([x[1] for x in self.raw_data[-30:]])/30 if len(self.raw_data)>=30 else -1)
        self.period =  int(sum([x[1] for x in self.raw_data])/len(self.raw_data))
