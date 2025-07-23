import json
import re
from typing import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from models import send_message_to_ollama, send_message_to_claude
from vector_db import semantic_search


class AgentState(TypedDict):
    primary_task: str
    current_task: str
    primary_answer: str
    attempts: int
    follow_up_question: str
    follow_up_task: str
    correct_answer: bool
    full_response: str
    full_reference: str
    subquestions: list[str]


# ✅ 1️⃣ Merged answer generation: detect type + generate answer in 1 call
def generate_answer(current_task: str):
    prompt = f"""
You are an AI Teaching Assistant.

1. Decide if the question is MCQ or FRQ.
2. Write the correct answer.

Respond in JSON:
{{"type": "MCQ", "answer": "<answer here>"}}

Question:
"{current_task}"
"""
    response = send_message_to_ollama(prompt)
    parsed = json.loads(response)
    print("Q TYPE:", parsed["type"])
    print("📌 Answer:", parsed["answer"])
    return parsed["answer"]


# ✅ 2️⃣ Merged classification: detect question/answer + relation in 1 call
def classify_message(state: AgentState):
    prompt = f"""
You are an AI Teaching Assistant.

Primary Question:
"{state['primary_task']}"

Student Message:
"{state['current_task']}"

Classify:
- "type": question or attempted_answer
- "relation": related or unrelated

Respond JSON:
{{"type": "question", "relation": "related"}}
"""
    response = send_message_to_claude(prompt)
    parsed = json.loads(response)
    return parsed["type"] == "question", parsed["relation"] == "unrelated"


# ✅ Redirect for unrelated
def redirect(state: AgentState):
    prompt = f"""
You've identified the student's message as unrelated.
Write a short reply that:
1. Acknowledges curiosity.
2. Suggests how it might relate.
3. Brings them back to the main question with a guiding question.

Original:
"{state['primary_task']}"

Unrelated:
"{state['current_task']}"
"""
    reply = send_message_to_ollama(prompt)
    state["full_response"] = reply
    return state


# ✅ Socratic follow-up
def follow_up(state: AgentState):
    guide = f"""
You are a Socratic Teaching Assistant.
Use the answer for context but do NOT reveal it.
Ask a guiding question to help the student think critically.

Main:
"{state['primary_task']}"

Correct Answer:
"{state['primary_answer']}"

Student's message:
"{state['current_task']}"
"""
    response = send_message_to_claude(guide)
    print("### FOLLOW-UP ###", response)
    state["full_response"] = response
    state["follow_up_question"] = extract_last_question(response)
    return state


# ✅ Grade answer
def grade_answer(state: AgentState):
    prompt = f"""
You are an AI Teaching Assistant.

If the answer is correct: confirm & encourage.
If incorrect: explain gently & ask a guiding question.

Main:
"{state['primary_task']}"

Student's Answer:
"{state['current_task']}"

Correct (internal only):
"{state['primary_answer']}"
"""
    response = send_message_to_claude(prompt)
    print("### GRADE ###", response)
    state["full_response"] = response
    state["correct_answer"] = is_correct(response)
    state["follow_up_question"] = extract_last_question(response)
    if state["correct_answer"]:
        state["attempts"] = 0
    return state


# ✅ Grade follow-up
def grade_follow_up(state: AgentState):
    prompt = f"""
You are an AI Teaching Assistant.

Main: {state['primary_task']}
Correct: {state['primary_answer']}
Follow-up: {state['follow_up_question']}
Student Follow-up Answer: {state['current_task']}

Respond without revealing the correct answer.
"""
    response = send_message_to_claude(prompt)
    print("### GRADE FOLLOW-UP ###", response)
    state["full_response"] = response
    state["follow_up_question"] = extract_last_question(response)
    return state


# ✅ Helpers
def extract_last_question(text: str):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    last = sentences[-1] if sentences else None
    return last if last and last.endswith("?") else None

def is_correct(text: str):
    return re.search(r"\b(correct|right)\b", text, re.IGNORECASE) is not None



def rag_support(text):
   
    retrieved_chunks = semantic_search(text)
    high_relevance_chunks = [
        chunk for chunk in retrieved_chunks if round(chunk.get("score", 0), 1) >= 0
    ]
    
    
    return high_relevance_chunks[0]["text"] if high_relevance_chunks else "No relevant content found."


# ✅ Nodes
def user_input(state: AgentState):
    if state["attempts"] == 0:
        state["primary_answer"] = generate_answer(state["current_task"])
    return state

def routing(state: AgentState):
    is_question, is_unrelated = classify_message(state)
    if is_question and is_unrelated:
        return "redirect"
    elif is_question:
        return "follow_up"
    elif state["follow_up_question"]:
        return "grade_follow_up"
    else:
        return "grade_answer"


# ✅ Graph
graph_builder = StateGraph(AgentState)

graph_builder.add_node("user_input", user_input)
graph_builder.add_node("redirect", redirect)
graph_builder.add_node("follow_up", follow_up)
graph_builder.add_node("grade_answer", grade_answer)
graph_builder.add_node("grade_follow_up", grade_follow_up)

graph_builder.add_conditional_edges(
    "user_input",
    routing,
    {
        "redirect": "redirect",
        "follow_up": "follow_up",
        "grade_follow_up": "grade_follow_up",
        "grade_answer": "grade_answer",
    },
)

graph_builder.set_entry_point("user_input")
graph = graph_builder.compile(checkpointer=InMemorySaver())


# ✅ Main driver
def run_question_step(user_message: str, session_state: dict):
    current_primary_task = session_state.get("primary_task") or user_message
    initial_input = {
        "primary_task": current_primary_task,
        "current_task": user_message,
        "primary_answer": session_state.get("primary_answer", ""),
        "attempts": session_state.get("attempts", 0),
        "follow_up_question": session_state.get("follow_up_question", ""),
        "follow_up_task": "",
        "correct_answer": False,
        "full_response": "",
        "full_reference": session_state.get("full_reference", ""),
        "subquestions": session_state.get("subquestions", []),
    }

    for s in graph.stream(initial_input, {"configurable": {"thread_id": "user-session-1"}}):
        final_state = s

    key = [k for k in final_state.keys() if k != "next"][0]
    updated = final_state[key]

    if updated["follow_up_question"] is None and updated["subquestions"]:
        updated["follow_up_question"] = updated["subquestions"].pop(0)

    return {
        **updated,
        "attempts": updated["attempts"] + 1,
    }
