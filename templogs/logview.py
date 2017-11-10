import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import matplotlib.dates as mdates
import sys
from matplotlib.collections import LineCollection
import numpy as np
import matplotlib.dates as md
import dateutil
from time import time
from datetime import datetime
from bisect import bisect_left, bisect_right
import sqlite3

class TempData:

    def __init__(self, logfile):
        self.raw_data = {}
        self.times = []
        conn = None
        try:
            conn = sqlite3.connect('..assistant/housecode.db')
            cur = conn.cursor()
            for x in cur.execute('select * from log'):
                if len(x) < 4:
                    x + ('OFF',)
                self.raw_data[int(x[0])] = [x[2], x[3] == "ON"]
                self.times.append(int(x[0]))
        except:
            print(sys.exc_info[0])
            sys.exit()
        if conn is not None:
            conn.close()

    def _get_range(self, mint, maxt=int(time())):
        times = self.times
        x = np.array(times[bisect_left(times, mint):bisect_right(times,maxt)])
        y = np.array([self.raw_data[t][0] for t in x])
        segments_x = np.r_[x[0], x[1:-1].repeat(2), x[-1]].reshape(-1, 2)
        segments_y = np.r_[y[0], y[1:-1].repeat(2), y[-1]].reshape(-1, 2)
        linecolors = ['red' if self.raw_data[x_[0]][1] else 'blue' for x_ in segments_x]
        segments = [list(zip(x_, y_)) for x_, y_ in zip(segments_x, segments_y)]
        return [segments,linecolors]


    def past_hours(self, hours):
        seconds = hours*3600 + 600
        mint = int(datetime.fromtimestamp(int(time()) - seconds).replace(minute=0,second=0).timestamp())
        xticks = self._x_ticks(mint,int(time()))
        print(xticks)
        return (self._get_range(xticks[0]), xticks)

    def today(self):
        return self.past_hours(max(datetime.now().hour, 8))

    def _show(self, toplot, xticks):
        plt.figure()
        ax = plt.axes()
        ax.add_collection(LineCollection(toplot[0], colors=toplot[1]))
        ax.set_xlim(xticks[0],toplot[0][-1][1][0])
        plt.xticks(xticks)
        ax.set_ylim(17,24)
        ax.xaxis.set_major_formatter(tick.FuncFormatter(self._readable_time))
        plt.grid(True)
        plt.show()

    def _x_ticks(self,minx,maxx):
        firsthour = int(datetime.fromtimestamp(minx).replace(minute = 0, second = 0).timestamp())
        firstday = int(datetime.fromtimestamp(minx).replace(hour=0, minute = 0, second = 0).timestamp())
        hours = int((maxx - minx)/3600)
        days = hours/24
        print(minx,maxx)
        if hours < 8:
            return range(firsthour,maxx,1800)
        elif hours < 24:
            return range(firsthour, maxx, 3600)
        elif 24 <= hours  < 40:
            return range(firstday, maxx, 3600*2)
        elif 40 <= hours  < 80:
            return range(firstday, maxx, 3600*4)
        elif 80 <= hours  < 160:
            return range(firstday, maxx, 3600*8)
        elif 160 <= hours  < 320:
            return range(firstday, maxx, 3600*12)
        elif 320 <= hours :
            return range(firstday, maxx, 3600*24)


    def show_hours(self, hours):
        toplot, xticks = self.past_hours(hours)
        self._show(toplot, xticks)

    def show_today(self):
        toplot, xticks = self.today()
        self._show(toplot, xticks)

    def _readable_time(self, timestamp, y=None):
        t = datetime.fromtimestamp(timestamp)
        if t.hour == t.minute == 0:
            return t.strftime("%a")
        elif t.minute != 0:
            return t.strftime("%H:%M")
        else:
            return t.strftime("%H")


temps = TempData("/home/pi/templogs/log")
if len(sys.argv) < 2:
    temps.show_today()
else:
    hours = int(sys.argv[1])
    temps.show_hours(hours)
