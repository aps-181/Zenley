import openai
import schedule
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Set up OpenAI client
client = openai.OpenAI(api_key=os.environ['OPEN_AI_KEY'])

# In-memory storage for user history
user_history = {}

def get_break_suggestion(user_id, session_duration):
    """Fetches a break suggestion while considering past suggestions."""

    # Retrieve user history
    history = user_history.get(user_id, [])

    # Construct conversation history
    messages = [{"role": "system", "content": "You are a health and productivity assistant. Suggest short, energizing activities like drinking water or stretching or a quick walk or looking away from the screen etc and avoid repetition."}]
    
    # Add past interactions (limit to last 5 to keep it short)
    for past in history[-5:]:  
        messages.append({"role": "user", "content": past["user"]})
        messages.append({"role": "assistant", "content": past["assistant"]})

    # Generate a dynamic prompt
    prompt = f"I have been working for {session_duration} minutes. Suggest an action which I could do to get energized."
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

    # Store response in history
    user_history.setdefault(user_id, []).append({"user": prompt, "assistant": suggestion})

    return suggestion

def schedule_breaks():
    """Schedules break recommendations for multiple users."""
    users = [
        {"id": 1, "session_duration": 90, "last_activity": "stretching"},
        {"id": 2, "session_duration": 60, "last_activity": "breathing exercises"},
    ]
    
    for user in users:
        get_break_suggestion(user["id"], user["session_duration"], user["last_activity"])

# # Run every 45 minutes
# schedule.every(1).minutes.do(schedule_breaks)

# print("AI Break Suggestion Service Running...")
# while True:
#     schedule.run_pending()
#     time.sleep(1)
