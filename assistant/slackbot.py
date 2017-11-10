import time
import json
from slackclient import SlackClient
from temperusb import temper
from pyHS100 import smartplug
import sys
dir1 = '/home/pi/assistant/hue'
sys.path.append(dir1)
from mycommands import commandDict, radiator, bedroom, stairs

#Import API Keys
with open('credentials.json') as f:
    credentials = json.load(f)
BOT_ID = 'U7G64J2AE'
BOT_NAME = 'housecode'
AT_BOT = "<@" + BOT_ID + ">"

slack_client = SlackClient(credentials['bot_token'])
triggers = commandDict.keys()

def parse_slack_output(slack_output):

    output_list = slack_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and (output['channel'] == 'D7G7RQHS8' or output["channel"] == "D7GCXDBFW") and output['user'] != 'U7G64J2AE':
                return output['text'].lower(), output['channel']
            if output and 'text' in output and AT_BOT in output['text']:
            # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
    return None, None

def handle_command(commandText, channel):
    response = ""
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
    if response:
        slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
        return

    for t in triggers:
        if commandText.startswith(t):
            extra = commandText.replace(t,"").strip()
            if extra:
                commandDict[t].run(extra)
            else:
                commandDict[t].run()
            response = "The trigger '%s' is running with '%s' argument" % (t, extra)
            slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
            return

    response = "Sorry, I don't know what you mean"
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
    # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    READ_WEBSOCKET_DELAY = 1

    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
