import time
import json
from slackclient import SlackClient
import sys

class Slack:
#Import API Keys
    def __init__(self):
        with open('credentials.json') as f:
            credentials = json.load(f)
            self.BOT_ID = credentials['bot_id']
            self.BOT_NAME = credentials['bot_name']
            self.AT_BOT = "<@" + self.BOT_ID + ">"
            self.slack_client = SlackClient(credentials['bot_token'])
    def parse_slack_output(self, slack_output):
        output_list = slack_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and (output['channel'] == 'D7G7RQHS8' or output["channel"] == "D7GCXDBFW") and output['user'] != self.BOT_ID:
                    return output['text'].lower(), output['channel']
                if output and 'text' in output and self.AT_BOT in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(self.AT_BOT)[1].strip().lower(), output['channel']
        return None, None
    def read(self):
        command, channel = self.parse_slack_output(self.slack_client.rtm_read())
        return command, channel
    def write(self, response, ch):
        self.slack_client.api_call("chat.postMessage", channel=ch, text=response, as_user=True)
    def isconnect(self):
        return self.slack_client.rtm_connect()
