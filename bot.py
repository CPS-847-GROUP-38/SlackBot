import slack
import os
from pathlib import Path
from dotenv import load_dotenv
# Import Flask
from flask import Flask
# Handles events from Slack
from slackeventsapi import SlackEventAdapter
from autocorrect import Speller
import requests
import json
import math

# Load the Token from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

key = os.environ['APIKEY']

# Configure your flask application
app = Flask(__name__)

# Configure SlackEventAdapter to handle events
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

# Using WebClient in slack, there are other clients built-in as well !!
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

# connect the bot to the channel in Slack Channel
# client.chat_postMessage(channel='#slack-bot', text='Send Message Demo')

# Get Bot ID
BOT_ID = client.api_call("auth.test")['user_id']

# handling Message Events
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')    
    text2 = event.get('text')
    
    spell = Speller(lang='en')
    
    if BOT_ID !=user_id:
        url = "https://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=%s" % (spell(text2),key)
        response = requests.get(url)
        data = json.loads(response.text)
        client.chat_postMessage(channel=channel_id, text=spell(text2))
        if data["cod"] != "404":
            print(data)
            if isinstance(math.ceil(data['main']['temp']), int) == True:
                client.chat_postMessage(channel=channel_id, text=str(math.ceil(data['main']['temp'])) + '°C')

# Run the webserver micro-service
if __name__ == "__main__":
    app.run(debug=True)
