import sqlite3
from datetime import date, datetime
from time import time, strftime, mktime, strptime
import sys


def parseData(rows):
    n = len(rows)
    for i in range(0,n,5):
        diff = (rows[i+5][1] - rows[i][1]) if i+5 < n else None
        average = (rows[i+5][1]+rows[i][1])/2 if i+5 < n else None
        if diff is not None:
            f.write("{0} {1} {2}/{3} {4} 0\n".format(rows[i][0], diff, rows[i][2], rows[i+5][2], rows[i][1]))

def parseData2(rows):
    n = len(rows)
    for i in range(0,n,3):
        diff = (rows[i+3][1] - rows[i][1]) if i+3 < n else None
        if diff is not None:
            f.write("{0} {1} {2}/{3} 0\n".format(rows[i][0], diff, rows[i][2], rows[i+3][2]))



gg = []
gg2 = []
conn = None
try:
    conn = sqlite3.connect('./assistant/housecode.db')
    cur = conn.cursor()
    for row in cur.execute('''select date, temp, status, lights from heaterstatus where date >= "2018-01-04 16:35:00" and date <= "2018-01-04 17:25:00"''' ):
        gg.append(row[0:3])
        #print("{0} - {1} - {2}".format(temp, status, lights))
    for row in cur.execute('''select date, temp, status, lights from heaterstatus where date >= "2018-01-04 18:50:00" and date <="2018-01-4 19:17:00"'''):
        gg2.append(row[0:3])
except:
    print(sys.exc_info()[0])
    pass

f = open('data_open_1.txt', 'w')

parseData(gg)
#parseData(gg2)
f.close()

