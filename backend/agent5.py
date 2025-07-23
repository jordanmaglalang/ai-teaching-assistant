import json
import re
from typing import TypedDict, Optional
from models import send_message_to_claude  # your Claude API wrapper

class AgentState(TypedDict):
    primary_task: str
    current_task: Optional[str]
    primary_answer: str
    attempts: int
    follow_up_question: Optional[str]
    follow_up_task: str
    correct_answer: bool
    full_response: str
    full_reference: Optional[str]
    subquestions: list[str]


def create_prompt(state: AgentState, user_message: str) -> str:
    # Compose a single large prompt incorporating all state and user input
    
    # Escape quotes in strings for safety in prompt
    def esc(text):
        return text.replace('"', '\\"') if text else ""

    prompt = f"""
You are an AI teaching assistant helping a student learn.

Current state of the session:
- Primary question/task: "{esc(state['primary_task'])}"
- Current user message: "{esc(user_message)}"
- Known correct answer (internal): "{esc(state['primary_answer'])}"
- Attempts made so far: {state['attempts']}
- Current follow-up question: "{esc(state['follow_up_question'])}"
- Remaining subquestions: {json.dumps(state['subquestions'])}

Your job is to:

1. Determine if the user's current message is a question or an attempted answer.
2. If it's a question, decide if it's related or unrelated to the primary question.
3. If unrelated, compose a polite redirect message bringing the student back on topic.
4. If an attempted answer, grade it against the correct answer:
   - Confirm and encourage if correct.
   - If incorrect, gently explain and ask a guiding follow-up question.
5. Update the follow-up question if needed.
6. Update the number of attempts.
7. Decide if the student's answer is correct (true/false).
8. Provide a helpful feedback message (full_response).
9. Optionally provide a relevant reference snippet (full_reference).
10. Update the subquestions list if any are answered or new follow-ups arise.

Respond only with a JSON object **exactly** in the following format (no extra commentary):

{{
  "is_question": true or false,
  "is_related": true or false,
  "correct_answer": true or false,
  "feedback": "Your detailed feedback message here.",
  "follow_up_question": "A new or updated follow-up question, or empty string if none.",
  "attempts": updated_attempts_integer,
  "primary_answer": "Updated correct answer if changed, else the same.",
  "subquestions": updated_subquestions_array,
  "full_reference": "Optional reference snippet or empty string."
}}

Here is the student's current message again:
"{esc(user_message)}"

Begin your response with the JSON object only.
"""
    return prompt


def parse_response(response_text: str) -> dict:
    """
    Parse the JSON response from Claude.
    Return a dictionary of updated state values.
    Raise error if JSON invalid.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        # Optionally log or raise with context
        raise ValueError(f"Failed to parse JSON from model response: {e}\nResponse text: {response_text}")


def run_question_step(user_message: str, session_state: AgentState) -> AgentState:
    """
    Run one step of the question answering conversation.
    Sends a giant prompt with all state and user input to Claude,
    then updates and returns the new session state.
    """

    # Ensure required keys in session_state with defaults
    state = {
        "primary_task": session_state.get("primary_task", user_message),
        "current_task": user_message,
        "primary_answer": session_state.get("primary_answer", ""),
        "attempts": session_state.get("attempts", 0),
        "follow_up_question": session_state.get("follow_up_question", ""),
        "follow_up_task": session_state.get("follow_up_task", ""),
        "correct_answer": session_state.get("correct_answer", False),
        "full_response": session_state.get("full_response", ""),
        "full_reference": session_state.get("full_reference", ""),
        "subquestions": session_state.get("subquestions", []),
    }

    prompt = create_prompt(state, user_message)
    print("DEBUG PROMPT:\n", prompt)

    raw_response = send_message_to_claude(prompt)
    print("RAW RESPONSE FROM CLAUDE:\n", raw_response)

    parsed = parse_response(raw_response)

    # Update state from parsed JSON
    state["correct_answer"] = parsed.get("correct_answer", state["correct_answer"])
    state["follow_up_question"] = parsed.get("follow_up_question", state["follow_up_question"])
    state["attempts"] = parsed.get("attempts", state["attempts"])
    state["primary_answer"] = parsed.get("primary_answer", state["primary_answer"])
    state["subquestions"] = parsed.get("subquestions", state["subquestions"])
    state["full_response"] = parsed.get("feedback", "")
    state["full_reference"] = parsed.get("full_reference", "")

    # You might want to reset attempts to 0 on correct answer
    if state["correct_answer"]:
        state["attempts"] = 0

    return state


# Optional helper for detecting last question (if you still want to use it)
def get_last_question(text: str) -> Optional[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return None
    last = sentences[-1]
    return last if last.endswith("?") else None
