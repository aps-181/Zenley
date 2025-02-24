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
    
 # Construct OpenAI messages with system, user, and assistant roles
    messages = [
        {"role": "system", "content":
         """ You are an ai chatbot that generates slack notifications for employees working from home or in an office to take short breaks and break activities, like a quick stretch or small exercies they could do for them to stay healthy and boost productivity.Ensure the message content varies from the last messages send. Don't suggest dance parties""" 
        }   
    ]

    # Include past break prompts and responses as message history
    for break_entry in reversed(past_breaks):  # Oldest first
        messages.append({"role": "user", "content": break_entry["prompt"]})
        messages.append({"role": "assistant", "content": break_entry["suggestion"]})

    # Add the latest request with dynamic session duration
    prompt = f"My last break was {session_duration} minutes ago and have been working since. What is a good break idea to get energized and stay healthy?"
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
