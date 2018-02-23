import time
import json
from temperusb import temper
from pyHS100 import smartplug
import sys
dir1 = '../templogs'
sys.path.append(dir1)
import percdata as perc
from mycommands import commandDict, radiator, bedroom, stairs
import classSlack

triggers = commandDict.keys()
slack = classSlack.Slack()
def handle_command(commandText, channel):
    response = ""
    try:
        if "temp" in commandText:
            temp = temper.TemperHandler().get_devices()[0].get_temperature()
            response = "The current temperature is %.2f and radiator is %s" % (temp, radiator.state)
        elif "radiator" in commandText:
            response = "The radiator is %s" % (radiator.state)
        elif "lucia" in commandText:
            response = "I just know Lucia is amazing, I don't have any other information, I'm sorry"
        elif "nicolas" in commandText and "home" in commandText:
            if bedroom.ison():
                response = "Probably yes"
            else:
                response = "Probably not"
        elif "average" in commandText:
            p = perc.PercData(60)
            response = "yesterday {0}%, last week {1}%, last 30 days {2}%, last 60 days {3}%".format(p.yesterday, p.lastWeek, p.lastmonth, p.period)
    except:
        response = str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])

    if response:
        slack.write(response, channel)
        return

    for t in triggers:
        if commandText.startswith(t):
            try:
                extra = commandText.replace(t,"").strip()
                if extra:
                    commandDict[t].run(extra)
                else:
                    commandDict[t].run()
                response = "The trigger '%s' is running" % (t)
            except:
                response = str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])
            slack.write(response, channel)
            return

    response = "Sorry, I don't know what you mean"
    slack.write(response, channel)

if __name__ == "__main__":
    #api_call = slack.slack_client.api_call("users.list")
    #if api_call.get('ok'):
     #retrieve all users so we can find our bot
        #users = api_call.get('members')
        #for user in users:
            #if 'name' in user and user.get('name') == slack.BOT_NAME:
                #print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    READ_WEBSOCKET_DELAY = 1

    if slack.isconnect():
        print("StarterBot connected and running!")
        while True:
            command, channel = slack.read()
            if command and channel:
                handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
