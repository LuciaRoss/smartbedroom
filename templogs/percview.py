import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import matplotlib.dates as md
from dateutil.relativedelta import *
from dateutil import parser
from time import time
from datetime import datetime, date

import sqlite3

class PercData:
    def __init__(self, period = None):
        self.raw_data = {}
        startdate = (date.today() + relativedelta(days=-period)).strftime("%Y-%m-%d") if period is not None else '1970-01-01'
        conn = sqlite3.connect('/home/pi/assistant/housecode.db')
        cur = conn.cursor()
        for row in cur.execute('''select * from heatpercentage where date >= ?''', (startdate, )):
            self.raw_data[parser.parse(row[0])] = row[1]
        self.raw_data = sorted(self.raw_data.items())
        conn.close()

    def _show(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        dates = [mdates.date2num(t[0]) for t in self.raw_data]
        y = [x[1] for x in self.raw_data]
        ax.set_xticks(dates)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
        ax.set_ylabel('ON time (%)')
        ax.plot_date(dates, y, linestyle='-',  marker='o', color='g')

        fig.autofmt_xdate(rotation=60)
        fig.tight_layout()
        ax.grid(True)
        plt.show()

if len(sys.argv) < 2:
    percs = PercData(30)
else:
    percs = PercData(int(sys.argv[1]))
percs._show()
