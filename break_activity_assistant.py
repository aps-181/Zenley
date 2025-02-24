import openai
import schedule
import os
from pathlib import Path
from dotenv import load_dotenv
from repository import get_last_break_suggestions, save_break_suggestion

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Set up OpenAI client
client = openai.OpenAI(api_key=os.environ['OPEN_AI_KEY'])

def get_break_suggestion(user_id, session_duration):
    """Fetches a break suggestion while considering past suggestions."""

    past_breaks = get_last_break_suggestions(user_id,3)

    #  """ You are an ai chatbot which acts like friend generating slack notifications for employees working from home or in an office asking them to take short breaks after work sessions and suggesting break activities, like a quick stretch or small exercies they could do for them to stay healthy and boost productivity.
    #        The suggestions should be in a fun and friendly manner. Consider the length of the user's work session when suggesting the break activity for the user to re charge. Suggest more physical activities when the session is longer than 45 minutes and suggest short breaks for smaller work sessions.
    #        Attach a wiki-how-to-do link of the exercises suggested if available.
    #        The message should not start with a hey or hi.
    #        Ensure the message content varies from the last messages send. Don't suggest dance parties""" 
    
 # Construct OpenAI messages with system, user, and assistant roles
    messages = [
        {"role": "system", "content":
         """ You are an ai chatbot which acts like friend generating slack notifications for employees working from home or in an office asking them to take short breaks after work sessions and suggesting break activities, like a quick stretch or small exercies they could do for them to stay healthy and boost productivity.
           The message should be structured in a light hearted, funny and friendly tone. Consider the length of the user's work session when suggesting the break activity for the user to re charge. 
           Suggest more heavy activities and a longer break of 10 or more minutes when the session is longer than 1 hour and suggest short breaks of 5 minutes with light activities for smaller work sessions lesser than 50 minutes.
           The message should not start with a hey or hi. Keep the messages short.
           Ensure the message content varies from the last messages send. Don't suggest dancing as an activity""" 
        }   
    ]

    # Include past break prompts and responses as message history
    for break_entry in reversed(past_breaks):  # Oldest first
        messages.append({"role": "user", "content": break_entry["prompt"]})
        messages.append({"role": "assistant", "content": break_entry["suggestion"]})

    # Add the latest request with dynamic session duration
    # if user_id =='U08AYDQ6YAU':
    #     session_duration=90
    # else:
    #     session_duration=45
    prompt = f"My last break was {session_duration} minutes ago and have been working since. What is a good break idea to get energized and stay healthy?"
    print(f"User id: {user_id} and prompt: {prompt}")
    messages.append({"role": "user", "content": prompt})
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=1.0
    )

    # Extract the AI's suggestion
    suggestion = response.choices[0].message.content
    print(f"User {user_id}: {suggestion}")

    save_break_suggestion(user_id,prompt,suggestion)

    return suggestion

# # Run every 45 minutes
# schedule.every(1).minutes.do(schedule_breaks)

# print("AI Break Suggestion Service Running...")
# while True:
#     schedule.run_pending()
#     time.sleep(1)
