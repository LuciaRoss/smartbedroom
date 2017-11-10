import sys
from datetime import date, datetime
from time import time, strftime, mktime, strptime
import sqlite3

conn = None
try:
    conn = sqlite3.connect('/home/pi/assistant/housecode.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS heatpercentage (date text, perc real)''')
    cur.execute('select max(date) from heatpercentage')
    startdate = cur.fetchone()[0]
    if startdate == None:
        startdate = '1970-01-01'
    enddate = datetime.fromtimestamp(time()).strftime("%Y-%m-%d")
    print("from {0} to {1}".format(startdate, enddate))
    dic = {}
    date_prec = ""
    sec_prec = 0
    sta_prec = 0
    rows = []

    for row in cur.execute('''select * from log where date > ? and date < ?''', (startdate,enddate,)):
        seconds = row[0]
        data = row[1].replace("'", "")
        status = row[3]

        if data in dic:
            if status == 'ON' and sta_prec == 'ON':
                tot = seconds - sec_prec
                dic[data] = dic[data] + seconds - sec_prec
            elif status == 'ON' and sta_prec == 'OFF':
                dic[data] = dic[data] + (seconds - sec_prec)/2
        else:
            if date_prec:
                perc = float("{0:.2f}".format(dic[date_prec]/86400.0*100))
                rows.append((date_prec, perc))
            if status == 'OFF':
                dic[data] = 0
            else:
                dic[data] = seconds - int(mktime(strptime(data, "%Y-%m-%d")))

        sec_prec = seconds
        sta_prec = status
        date_prec = data

    if date_prec in dic:
        perc = float("{0:.2f}".format(dic[date_prec]/86400.0*100))
        rows.append((date_prec, perc))

    print(len(rows))
    if len(rows) > 0:
        cur.executemany('''INSERT INTO heatpercentage ('date', 'perc') VALUES (?, ?)''', rows)
        conn.commit()
    conn.close()
    print('SUCCESS')

except NameError as e:
    print(e)
    pass
except:
    print(sys.exc_info()[0])
    print('ERROR')
    pass

