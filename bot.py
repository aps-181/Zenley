import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datetime import datetime, timedelta
from views import get_app_home_tab_view
from google_calendar import google_calendar_details, calendar_api_request

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

app = Flask(__name__)
app.register_blueprint(google_calendar_details)

app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

dbData = [
    {
        "userId": "U08AYDQ6YAU",
        "messageScheduledTime": datetime.now(),
        "intervalInSeconds": 20,
        "credentials": None
    }
]

messages = [
    "Getting up from chair",
    "Have some water",
    "Take a walk"
]

index = 0


@app.route("/")
def home():
    return "Testing"


@app.route("/connectToGoogleCalendar", methods=["POST"])
def connect_to_google_calendar():
    try:
        btn_click_interaction_payload = request.form.get("payload")
        print("Payload: \n", btn_click_interaction_payload)
        return '', 200

    except Exception as e:
        print("Error connecting to google calendar >>> ", format(e))


@app.route("/processEvents", methods=["POST"])
def processEvents():
    try:
        slack_event = request.json
        if "challenge" in slack_event:
            return slack_event["challenge"], 200

        if slack_event.get('event', {}).get('type') == 'app_home_opened':
            user_id = slack_event['event']['user']
            # Call the function to send the Home tab
            send_app_home_tab(user_id)

        return '', 200

    except Exception as e:
        print("Error:  >>>> \n", format(e))


def send_app_home_tab(user_id):
    home_tab_view = get_app_home_tab_view(user_id)
    try:
        result = client.views_publish(
            user_id=user_id,
            view=home_tab_view
        )
        print("App home view result >>> ", result)

    except Exception as e:
        print("Error while sending app_home_view", format(e))


def scheduleNotification():
    print("Endered notification scheduler ")
    for entry in dbData:
        # try:
        #     calendar_api_request()
        # except Exception as e:
        #     print("Got an error", format(e))
        currentTime = datetime.now()
        messageScheduledTime = entry["messageScheduledTime"]
        intervalInSeconds = entry["intervalInSeconds"]
        userId = entry["userId"]
        if messageScheduledTime < currentTime:
            print("Updating messageScheduledTime")
            messageScheduledTime = currentTime + timedelta(seconds=intervalInSeconds)
            scheduleMessage(userId, messageScheduledTime)
            entry["messageScheduledTime"] = messageScheduledTime
            print("New messageScheduledTime time", messageScheduledTime)


def scheduleMessage(id, scheduled_timestamp):
    try:
        # Call the chat.scheduleMessage method using the WebClient
        global index
        messageToSend = messages[index]
        index = index+1
        if index == 3:
            index = 0

        result = client.chat_scheduleMessage(
            channel=id,
            text=messageToSend,
            post_at=scheduled_timestamp.strftime('%s')
        )
        # Log the result
        print("Message Scheduled")

    except slack.SlackApiError as e:
        print("Error scheduling message: {}".format(e))


scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduleNotification, trigger="interval", seconds=10)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # This disables the requested scopes and granted scopes check.
    # If users only grant partial request, the warning would not be thrown.
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

    app.run(host='0.0.0.0', port=5000, debug=True)
