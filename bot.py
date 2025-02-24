import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datetime import datetime, timedelta
from views import get_app_home_tab_view
from google_calendar import google_calendar_details, get_calendar_events
from break_activity_assistant import get_break_suggestion
from repository import initalize_user_session, fetch_all_user_sessions, update_user_sessions

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

app = Flask(__name__)
app.register_blueprint(google_calendar_details)

app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

user_message_details = []


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
def process_events():
    try:
        slack_event = request.json
        if "challenge" in slack_event:
            return slack_event["challenge"], 200

        if slack_event.get('event', {}).get('type') == 'app_home_opened':
            user_id = slack_event['event']['user']
            # Call the function to send the Home tab
            send_app_home_tab(user_id)

        if slack_event.get('event', {}).get('type') == 'user_status_changed':
            user_id = slack_event['event']['user']
            # Call the function to send the Home tab
            # send_app_home_tab(user_id)
            print("Slack event: ", slack_event,
                  "\n user Id: ", user_id, end="\n")

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
        print("Send app home tab view")

    except Exception as e:
        print("Error while sending app_home_view", format(e))

def schedule_notification():
    print("Entered notification scheduler ")

    user_sessions = fetch_all_user_sessions()
    users_sessions_to_update = []

    if not user_sessions:
        print("No users found in db when trying to post messages, hence returning")
        return
    
    for user in user_sessions:
        user_id = user['user_id']

        if not user["is_active"]:
            continue

        current_time = datetime.now()
        user_current_session_duration = current_time - user["session_start_time"]
        print("User session time: ",(user_current_session_duration/60))
        user_session_duration_in_minutes = int(user_current_session_duration.total_seconds()/60)
        
        if user_current_session_duration > timedelta(minutes=1):
            
            message = f"Hey <@{user_id}> you seem to be working continously for the past {user_session_duration_in_minutes} minutes. " + get_break_suggestion(user_id, 45)
            is_success = post_messgae(user_id,message)
            if(is_success):
                user["session_start_time"] = datetime.now()
                users_sessions_to_update.append(user)
                print("Updated session time to ",user["session_start_time"], "for user ", user_id)
        
    update_user_sessions(users_sessions_to_update)

            



def post_messgae(user_id,message):
    if user_id == "U08C98PGANS": 
        print("Skipping message posting")
        return
    try:
        # Call the chat.postMessage method using the WebClient
        result = client.chat_postMessage(
            channel=user_id, 
            text=message
        )
        print(f"Posted message: {message} to user {user_id}")
        return result["ok"]
    except Exception as e:
        print(f"Failed to post message for user id, {user_id} due to error: {e}")
        return False


message_scheduler = BackgroundScheduler()
message_scheduler.add_job(func=schedule_notification, trigger="interval", seconds=120)
message_scheduler.start()

def is_bot_user(user):
    return user["is_bot"] or user["real_name"] == "Slackbot"

def get_workspace_members():
    try:
        result = client.users_list()
        if result["ok"]:
           members = result["members"] 
           app_users = [member for member in members if not is_bot_user(member)]
           initalize_user_session(app_users)
          
    except Exception as e:
        print("An exception occured while getting workspace users: ", format(e))


def poll_member_presence():
    user_sessions = fetch_all_user_sessions()
    if not user_sessions:
        get_workspace_members()

    users_sessions_to_update = []
    for user in user_sessions:
        user_id = user["user_id"]
        try:
            result = client.users_getPresence(user=user_id)
            if result["ok"]:
                if result["presence"] == "active" and not user["is_active"]:
                    user["session_start_time"] = datetime.now()
                    user["is_active"] = True
                    users_sessions_to_update.append(user)
                elif result["presence"] != "active" and user["is_active"]:
                    user["session_end_time"] = datetime.now()
                    user["is_active"] = False
                    users_sessions_to_update.append(user)

            print(f"User {user_id} is: ", result)
        except Exception as e:
            print("Error occured while polling user status: ",user_id,"Error: ",format(e),end="\n")
    update_user_sessions(users_sessions_to_update)
    for user in user_sessions:
        print("Current user status: ", user, end = "\n")


user_presence_check_scheduler = BackgroundScheduler()
user_presence_check_scheduler.add_job(func=poll_member_presence, trigger="interval", seconds=60)
user_presence_check_scheduler.start()

# Shut down the schedulers when exiting the app
atexit.register(lambda: user_presence_check_scheduler.shutdown())
atexit.register(lambda: message_scheduler.shutdown())

if __name__ == "__main__":
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # This disables the requested scopes and granted scopes check.
    # If users only grant partial request, the warning would not be thrown.
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

    app.run(host='0.0.0.0', port=5000, debug=True,use_reloader=False)
