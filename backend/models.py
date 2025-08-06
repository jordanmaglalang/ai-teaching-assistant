import anthropic
import os
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from together import Together

# Load environment variables
_ = load_dotenv()
GPT_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None
gpt_model = ChatOpenAI() if GPT_API_KEY else None
client2 = Together(api_key=TOGETHER_API_KEY) if TOGETHER_API_KEY else None

# ✅ Toggle this for real vs. mock mode
MOCK_MODE = True

def send_message_to_claude(user_message: str):
    if MOCK_MODE:
        print("🧪 [MOCK Claude] Prompt:", user_message)
        # Return simple fake results based on content
        if "Classify" in user_message or "question or attempted_answer" in user_message:
            return "question"
        if "related or unrelated" in user_message:
            return "related"
        if "redirect" in user_message:
            return "I appreciate your curiosity! But let’s get back to our main topic: What do you think the mitochondria does?"
        if "Socratic" in user_message or "guiding question" in user_message:
            return "Interesting thought. What do you think causes this process to happen?"
        if "yes" in user_message:
            return "You are right!"
        return "This is a mock Claude response. What would you like to know? Maybe about the mitochondria? Or the cell structure? Or something else? Let's keep it simple and focused on biology.   What do you think the mitochondria does?  What is the role of the mitochondria in a cell? What do you think the mitochondria does? What do you think the mitochondria does? What do you think the mitochondria does? What do you think the mitochondria does? What do you think the mitochondria does? What do you think the mitochondria does? What do you think the mitochondria does? What do you think the mitochondria does?"
    else:
        response = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text

def send_message_to_mixtral(prompt):
    if MOCK_MODE:
        print("🧪 [MOCK Mixtral] Prompt:", prompt)
        # Return plausible dummy MCQ/FRQ output
        if "MCQ" in prompt:
            return "Type: MCQ\nAnswer: B"
        elif "FRQ" in prompt:
            return "Type: FRQ\nAnswer: The mitochondria is the powerhouse of the cell."
        return random.choice([
            "Type: MCQ\nAnswer: A",
            "Type: FRQ\nAnswer: This is a sample free response answer."
        ])
    else:
        response = client2.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
import requests

def send_message_to_ollama(prompt: str, model: str = "llama3") -> str:
    """
    Call your local Ollama server with a prompt.
    Requires Ollama to be running locally: ollama serve

    Args:
        prompt (str): Your prompt text.
        model (str): The local model to use, e.g. 'llama3' or 'phi3'.

    Returns:
        str: The model's reply as plain text.
    """
    if MOCK_MODE:
        print("🧪 [MOCK Ollama] Prompt:", prompt)
        # Return simple mock output based on prompt type
        if "multiple-choice" in prompt.lower():
            return "MCQ"
        if "free response" in prompt.lower():
            return "FRQ"
        if "classify" in prompt.lower():
            return "question"
        if "concept" in prompt.lower():
            return "pointers, dereference, uninitialized, segmentation fault"
        return "This is a mock Ollama response."
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False  # we want full output in one go
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()

    return result.get("response", "").strip()
