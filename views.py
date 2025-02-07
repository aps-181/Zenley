def get_app_home_tab_view(user_id):
    home_tab_view = {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "block_id": "zenley_welcome_section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Welcome to Zenle!* :purple_heart:\nYour friendly assistant for keeping you on track with reminders to take breaks, hydrate, and exercise. Zenley will help you stay productive and healthy throughout the day!"
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://example.com/zenley-logo.png",  # Replace with your actual image URL
                    "alt_text": "Zenley logo"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "block_id": "zenley_intro_section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*How Zenley helps you:*\n\n• *Reminders to take breaks*\n• *Hydration alerts to drink water*\n• *Exercise nudges to stay active*\n• *Customizable reminders to fit your routine*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "block_id": "zenley_actions_section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*What would you like to do today?* :sparkles:\nChoose an action below to get started!"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Set My First Reminder"
                    },
                    "action_id": "set_first_reminder"
                }
            },
            {
                "type": "section",
                "block_id": "zenley_feedback_section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Need help?* :question:\nIf you need any assistance or have questions, feel free to reach out to Zenley support!"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Connect my Google Calendar"
                    },
                    "action_id": "contact_support",
                    "url":f"https://rngyq-59-88-174-18.a.free.pinggy.link/authorize?user_id={user_id}"
                }
            }
        ]
    }
    

    return home_tab_view