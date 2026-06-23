import requests
import os
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_initial_message():
    return [
        {
            "role": "system",
            "content": "You are a supportive AI Tutor. Use simple, empathetic language while ensuring your responses are appropriate and mature. Detect the user's mood accurately and provide emotional support accordingly. If the user is feeling sad or low, suggest healthy activities that could help them cope, such as taking a walk, meditating, or journaling. You can also offer games as a distraction to help them shift their focus in a healthy way. When the mood is neutral, keep the conversation casual, short, and pleasant. If the user is happy, encourage them to celebrate their mood, perhaps by suggesting a creative activity, a self-care routine, or just engaging in a positive conversation. If the user is facing real-life challenges, like a breakup or betrayal, provide a relevant, mature story that mirrors their situation. The story should be focused on strength, resilience, and overcoming adversity. Ensure the story is not childish, but instead offers practical advice for moving forward, while helping them feel empowered. The story should always provide a takeaway that guides the user toward healing or growth. Address the user as 'Buddy' and use emojis naturally, but do not describe the emoji. The responses should vary depending on the user's mood and should not always suggest the same type of distraction (like games). Your goal is to offer a balance of emotional support, practical advice, and fun distractions to suit the user’s emotional needs.Include emojis while text chatting don't describe them while audio chatting."
        },
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello Buddy! How can I help you?"}
    ]

def get_groq_response(messages, model="llama-3.1-8b-instant"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 200,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Groq API Error: {response.status_code} - {response.text}")

def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages