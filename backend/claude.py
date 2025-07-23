
import anthropic
import os

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def send_message_to_claude(user_message: str):
    response = client.messages.create(
        model="claude-3.5-sonnet-20240620",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text

# Usage

