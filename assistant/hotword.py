#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function
import sqlite3
import argparse
import os.path
import json
from logger import Logger
from mycommands import commandDict,sceneCommandDict,refreshScenes
from time import time
import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

logger = Logger()
triggers = commandDict.keys()

def createDatabase():
    conn = sqlite3.connect('housecode.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS vacationmode (id int, mode text, end text, hdate text) ')
    c.execute("INSERT INTO vacationmode VALUES ( ?, 'False', 'None', 'None' )", (str(int(time())),))
    c.execute('''CREATE TABLE IF NOT EXISTS heaterstatus (seconds int, date text, temp real, status text, lights text, desc text)''')
    conn.commit()
    conn.close()

def runcommand(trigger, commandobj, spokentext):
    extra = spokentext.replace(trigger.lower(),"").strip()
    if extra:
        commandobj.run(extra)
    else:
        commandobj.run()

def process_event(event, assistant):
    """Pretty prints events.

    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.

    Args:
        event(event.Event): The current event to process.
    """
    print(event)

    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        refreshScenes()
        print("refreshed scenes")


    if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
        text = event.args['text'].lower().strip()
        print("you said:   "+text)
        logger.log("SAID:  "+text)
        for t in triggers:
            if text.startswith(t):
                runcommand(t,commandDict[t],text)
                print("RUNNING {0} WITH {1}".format(t,text))
                assistant.stop_conversation()
                return
        for t2 in sceneCommandDict.keys():
            if text.startswith(t2):
                torun = sceneCommandDict[t2]
                print("Setting Scene to {}".format(t2))
                torun.run(t2)
                assistant.stop_conversation()
                return

    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        print()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='Path to store and read OAuth2 credentials')
    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))
    createDatabase()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(event, assistant)


if __name__ == '__main__':
    main()
