import anthropic
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from together import Together
# Load environment variables
_ = load_dotenv()
GPT_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
gpt_model = ChatOpenAI()
client2 = Together(api_key=TOGETHER_API_KEY)

def send_message_to_claude(user_message: str):
    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text



def send_message_to_mixtral(prompt):
    response = client2.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
#message = send_message_to_mixtral("explain the difference between a for loop and a while loop in python")
#print(message)