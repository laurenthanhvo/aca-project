import logging
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Set up logging and load environment variables
logging.basicConfig(level=logging.INFO)
load_dotenv()

# Retrieve Slack tokens from environment variables
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]

# Initialize the Slack app
app = App(token=SLACK_BOT_TOKEN)

# Define the dictionary to store user achievements
user_achievements = {}

# Function to get the time of day greeting
def get_time_greeting():
    current_time = datetime.now().time()
    if current_time < datetime.strptime("12:00:00", "%H:%M:%S").time():
        return "morning"
    elif current_time < datetime.strptime("18:00:00", "%H:%M:%S").time():
        return "afternoon"
    else:
        return "evening"

# List of uplifting messages for random dose of happiness
uplifting_messages = [
    "Your potential is limitless. 🌟",
    "Embrace the journey, one step at a time. 🌱",
    "\"Be yourself; everyone else is already taken.\" - Oscar Wilde 🌈",
    "Embrace the challenges. They make you stronger. 💪",
    "\"What you think, you become. What you feel, you attract. What you imagine, you create.\" - Buddha 🌼",
    "\"You have within you right now, everything you need to deal with whatever the world can throw at you.\" - Brian Tracy 🌞",
    "The smallest step in the right direction can turn out to be the biggest step of your life. 🚀",
    "\"The only way to do great work is to love what you do.\" - Steve Jobs❤️",
    "\"Success is not final, failure is not fatal: It is the courage to continue that counts.\" - Winston Churchill 🌟",
]

# Function to handle app mentions and achievements command
@app.event("app_mention")
def mention_handler(body, say, event, ack):
    ack()
    user_name = event.get("user", "")
    user_info = app.client.users_info(user=user_name)
    real_name = user_info["user"]["real_name"] if user_info["ok"] else ""
    
    if real_name:
        text = event.get("text", "")
        if "/doseofhappy" in text:
            # Provide a random dose of happiness
            random_message = random.choice(uplifting_messages)
            say(f"Here's your dose of happiness, {real_name}:\n>{random_message}")
        elif "/achievements log" in text:
            # Log a new achievement and remove prefix if present
            achievement = text[len("/achievements log"):].strip()
            prefix_to_remove = "chievements log "
            cleaned_achievement = achievement.replace(prefix_to_remove, "")
            if user_name not in user_achievements:
                user_achievements[user_name] = []
            user_achievements[user_name].append(achievement)
            say(f"Great job, {real_name}! You've logged a new achievement: {cleaned_achievement}")
        elif "/achievements view" in text:
            if user_name in user_achievements:
                achievements_list = "\n".join(user_achievements[user_name])
                if achievements_list:
                    # Remove prefix and show user achievements
                    prefix_to_remove = "chievements log "
                    cleaned_achievements_list = [a.replace(prefix_to_remove, "") for a in achievements_list.split("\n")]
                    cleaned_achievements_text = "\n".join(cleaned_achievements_list)
                    say(f"{real_name}, here are your logged achievements:\n>{cleaned_achievements_text}")
                else:
                    say(f"{real_name}, you haven't logged any achievements yet. Keep up the good work!")
            else:
                say(f"{real_name}, you haven't logged any achievements yet. Keep up the good work!")
        elif "/achievements clear" in text:
            if user_name in user_achievements:
                # Clear user achievements and encourage a fresh start
                user_achievements[user_name] = []
                say(f"{real_name}, a new chapter begins! 🌟 Your achievements have been cleared, giving you a blank canvas to paint your future successes. 🚀")
            else:
                say(f"{real_name}, you haven't logged any achievements yet. Keep up the good work!")
        else:
            # Handle default greetings if real name is not available
            handle_default_greeting(say, real_name, user_name)

# Function to handle default greetings
def handle_default_greeting(say, real_name, user_name):
    time_greeting = get_time_greeting()
    emoji = "🌼" if time_greeting == "morning" else "🌞" if time_greeting == "afternoon" else "🌙"
    if user_name in user_achievements:
        achievements_list = "\n".join(user_achievements[user_name])
        say(f"Good {time_greeting}, {real_name}! Here are your achievements:\n>{achievements_list}\nHave a {emoji} day!")
    else:
        say(f"Good {time_greeting}, {real_name}! Have a {emoji} day!")

@app.event("message")
def message_handler(body, context, payload, options, say, event):
    pass

if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
