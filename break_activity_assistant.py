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

    last_suggestions = get_last_break_suggestions(user_id,5)
    
    prompt = f"""
    I have been working for {session_duration} minutes since my last break.
    In my past five breaks, I have done: {', '.join(last_suggestions)}.

    Suggest an energizing and motivating break activity that also keeps me healthy 
    by preventing backaches, migraines, or dehydration. 
    Ensure variety, usefulness and doable in an office setting.
    """


    # Construct conversation history
    messages = [{"role": "system", "content": "You are a health and productivity assistant. Suggest short, energizing activities like drinking water or stretching or a quick walk or looking away from the screen etc and avoid repetition."}]
    
    # # Add past interactions (limit to last 5 to keep it short)
    # for past in history[-5:]:  
    #     messages.append({"role": "user", "content": past["user"]})
    #     messages.append({"role": "assistant", "content": past["assistant"]})

    # Generate a dynamic prompt
    # prompt = f"I have been working for {session_duration} minutes. Suggest an action which I could do to get energized."
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

    save_break_suggestion(user_id,suggestion)

    return suggestion

# # Run every 45 minutes
# schedule.every(1).minutes.do(schedule_breaks)

# print("AI Break Suggestion Service Running...")
# while True:
#     schedule.run_pending()
#     time.sleep(1)
