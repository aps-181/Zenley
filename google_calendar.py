# -*- coding: utf-8 -*-

import os
import flask
from flask import Blueprint, request
from datetime import datetime, time
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# The OAuth 2.0 access scope allows for access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

Redirect_URI = "https://rngyq-59-88-174-18.a.free.pinggy.link/oauth2callback"

db_credentials_dummy = None
isCalendarPermissionGranted = False


google_calendar_details = Blueprint('google_calendar_details',__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
# google_calendar_details.secret_key = 'REPLACE ME - this value is here as a placeholder.'



def calendar_api_request():
    # if 'features' not in flask.session  or 'credentials' not in flask.session:
    if not isCalendarPermissionGranted  or not db_credentials_dummy:
            print("\n>>>>>>>\nCame inside if block since credentials are not there\n >>>>>>>\n")
            return flask.redirect('authorize')

   
    # features = flask.session['features']

    # if features['calendar'] and flask.session['credentials']:
    if isCalendarPermissionGranted and db_credentials_dummy:
             print("\n >>>>>>\nCame inside if block after getting credentials \n>>> \n")
            # # User authorized Calendar read permission.
            # # Calling the APIs, etc.
            # return ('<p>User granted the Google Calendar read permission. ' +
            #         'This sample code does not include code to call Calendar</p>')
             try:
                service = build("calendar", "v3", credentials = google.oauth2.credentials.Credentials(
        **db_credentials_dummy) )
                # Call the Calendar API
                now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
                today = datetime.today().date()
                eight_am = datetime.combine(today, time(5, 0)).isoformat() + "Z"  # 'Z' indicates UTC time
                # Create a time object for 6 PM (18:00)
                six_pm = datetime.combine(today, time(13, 30)).isoformat() + "Z"  # 'Z' indicates UTC time
                print("Getting the upcoming 10 events")
                events_result = (
                    service.events()
                    .list(
                        calendarId="primary",
                        timeMin=eight_am,
                        timeMax = six_pm,
                        maxResults=10,
                        singleEvents=True,
                        orderBy="startTime",
                        timeZone = "UTC"
                    )
                    .execute()
                )
                events = events_result.get("items", [])

                if not events:
                  print("No upcoming events found.")
                  return "No upcoming events found."

                # Prints the start and name of the next 10 events
                for event in events:
                  start_time = event["start"].get("dateTime")
                  end_time = event["end"].get("dateTime")
                  print("Start: ", start_time, end="\n")
                  print("End ", end_time)

                return "Got the events"

             except HttpError as e:
                 print(f"An error occurred >>>>>>>>>>>>>>>>>> \n:", format(e))
    
    else:
            # User didn't authorize Calendar read permission.
            # Update UX and application accordingly
            return '<p>Calendar feature is not enabled.</p>'


@google_calendar_details.route('/authorize')
def authorize():
    # user_id = request.args.get('user_id')
    print("\nUser id : ",request.args.get("user_id"),end="\n")
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = Redirect_URI
   
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@google_calendar_details.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    # flow.redirect_uri = flask.url_for('google_calendar_details.oauth2callback', _external=True)
    flow.redirect_uri = Redirect_URI

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    credentials = credentials_to_dict(credentials)
    flask.session['credentials'] = credentials
    global db_credentials_dummy 
    db_credentials_dummy = credentials
    global isCalendarPermissionGranted
    isCalendarPermissionGranted = True

    # Check which scopes user granted
    features = check_granted_scopes(credentials)
    flask.session['features'] = features
    return flask.redirect('/')


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'granted_scopes': credentials.granted_scopes}


def check_granted_scopes(credentials):
    features = {}
    if 'https://www.googleapis.com/auth/calendar.readonly' in credentials['granted_scopes']:
        features['calendar'] = True
    else:
        features['calendar'] = False

    return features


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # This disables the requested scopes and granted scopes check.
    # If users only grant partial request, the warning would not be thrown.
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    # google_calendar_details.run(host='0.0.0.0', port=8080, debug=True)
