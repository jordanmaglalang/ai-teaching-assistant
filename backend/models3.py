import anthropic
import os
import random
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from together import Together

# Load .env
load_dotenv()
GPT_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

client_claude = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
client_mixtral = Together(api_key=TOGETHER_API_KEY)
gpt_model = ChatOpenAI()

MOCK_MODE = False

# ----------------------------
# Claude: Streaming version
# ----------------------------

def send_message_to_claude(prompt: str) -> str:
    if MOCK_MODE:
        print("🧪 [MOCK Claude] Prompt:", prompt)
        if "Classify" in prompt or "attempted_answer" in prompt:
            return "question"
        if "related or unrelated" in prompt:
            return "related"
        if "redirect" in prompt:
            return "I appreciate your curiosity! Let’s get back to our main topic: What do you think the mitochondria does?"
        if "Socratic" in prompt or "guiding question" in prompt:
            return "Interesting thought. What do you think causes this process to happen?"
        return "This is a mock Claude streaming response. What do you think the mitochondria does?"

    # Use streaming version
    full_response = ""
    with client_claude.messages.stream(
        model="claude-opus-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for chunk in stream:
            # Claude sends `content_block_delta`
            if chunk.type == "content_block_delta":
                full_response += chunk.delta.text

    return full_response.strip()

# ----------------------------
# Mixtral
# ----------------------------

def send_message_to_mixtral(prompt: str) -> str:
    if MOCK_MODE:
        print("🧪 [MOCK Mixtral] Prompt:", prompt)
        if "MCQ" in prompt:
            return "Type: MCQ\nAnswer: B"
        if "FRQ" in prompt:
            return "Type: FRQ\nAnswer: The mitochondria is the powerhouse of the cell."
        return random.choice([
            "Type: MCQ\nAnswer: A",
            "Type: FRQ\nAnswer: This is a sample free response answer."
        ])

    response = client_mixtral.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

# ----------------------------
# Ollama
# ----------------------------

def send_message_to_ollama(prompt: str, model: str = "llama3") -> str:
    if MOCK_MODE:
        print("🧪 [MOCK Ollama] Prompt:", prompt)
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
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        print(f"[Ollama Error] {e}")
        return "Ollama error."
