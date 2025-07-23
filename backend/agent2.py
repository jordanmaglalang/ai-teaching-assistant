from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage
from models import send_message_to_claude, send_message_to_mixtral, send_message_to_ollama
from typing import Annotated, TypedDict
from langchain.agents import initialize_agent, AgentType
from vector_db import semantic_search
import re
from tools import retrieve_relevant_chunks, create_question

tools = [retrieve_relevant_chunks, create_question]
# NOTE: `model_with_tools` is only used in grade_answer — you may want to adjust that too
# But for now, we’ll leave it since you’re only swapping text generation calls
"""
model_with_tools = initialize_agent(
    tools=tools,
    llm=None,  # No GPT model here
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)
"""
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

def user_input(state: AgentState):
    if state["attempts"] == 0:
        state["primary_answer"] = generate_answer(state["current_task"])
        print("#CURRENT PRIMARY ANSWER#", state["primary_answer"])
    return state

def user_input2(state: AgentState):
    return state

def user_input3(state: AgentState):
    return state

def user_input4(state: AgentState):
    return state

def generate_answer(current_task):
    question_type_prompt = f"""
You are an AI assistant helping classify student questions.
Your task is to determine whether the following question is:

- A multiple-choice question (MCQ)
- A free response question (FRQ)

Respond only with: "MCQ" or "FRQ"

Question:
"{current_task}"
""".strip()

    mcq_prompt = f"""
You are a highly knowledgeable teaching assistant.

The student question is **multiple-choice**.
Your task:
1. Identify the correct answer choice (A, B, C, D, etc.)
2. State it clearly.

Question:
"{current_task}"
""".strip()

    frq_prompt = f"""
You are a highly knowledgeable teaching assistant.

The student question is **free response**.
Your task:
1. Provide a clear, concise answer in your own words.
2. Use simple language.

Question:
"{current_task}"
""".strip()

    response1 = send_message_to_ollama(question_type_prompt)
    q_type = response1.strip().lower()
    print("Q TYPE IS", q_type)

    if q_type == "frq":
        response2 = send_message_to_ollama(frq_prompt)
    else:
        response2 = send_message_to_ollama(mcq_prompt)

    print("📌 Stored correct answer:", response2.strip())
    return response2.strip()

def classify_task_type(state: AgentState):
    current_task = state["current_task"]
    classification_prompt = f"""
You are an AI assistant classifying student input.

Classify the student's message as one of:
- question
- attempted_answer

Message:
"{current_task}"

Examples:
"What is a function?" → question
"I think it's photosynthesis." → attempted_answer

Respond with: question or attempted_answer
""".strip()

    response = send_message_to_ollama(classification_prompt)
    result = response.strip().lower().strip(".")
    return result == "question"

def question_type(state: AgentState):
    primary_task = state['primary_task']
    current_task = state['current_task']
    follow_up = state["follow_up_question"] if state["follow_up_question"] else None

    question_type_prompt = f"""
You are an AI Teaching Assistant.

Decide if the student's message is:
- related (builds on the same topic)
- unrelated (switches to a different topic)

Primary Question:
"{primary_task}"

Follow Up:
"{follow_up}"

Student Message:
"{current_task}"

Respond with: related or unrelated
""".strip()

    response = send_message_to_ollama(question_type_prompt)
    result = response.strip().lower().strip(".")
    return result == "unrelated"

def redirect(state: AgentState):
    primary_task = state["primary_task"]
    current_task = state["current_task"]

    redirect_prompt = f"""
You've identified the student's message as unrelated.
Write a short reply that:
1. Acknowledges curiosity.
2. Suggests how it might relate.
3. Brings them back to the main question with a guiding question.

Original:
"{primary_task}"

Unrelated:
"{current_task}"
""".strip()

    response = send_message_to_ollama(redirect_prompt)
    print("##REDIRECT##", response)
    state["full_response"] = response
    return state

def follow_up(state: AgentState):
    primary_task = state["primary_task"]
    current_task = state["current_task"]
    primary_answer = state["primary_answer"]

    guide = f"""
You are a Socratic AI Teaching Assistant.
Use the correct answer for context but DO NOT reveal it.
Ask a guiding question to help the student think critically.

Main Question:
"{primary_task}"

Correct Answer:
"{primary_answer}"

Student's confusion:
"{current_task}"
""".strip()

    response = send_message_to_claude(guide)
    print("###FEEDBACK RESPONSE###", response)
    state["full_response"] = response
    state["follow_up_question"] = get_last_question(response)
    return state

def answer_type(state: AgentState):
    return bool(state["follow_up_question"])

def follow_up_type(state: AgentState):
    return bool(state["follow_up_question"])

def grade_follow_up(state: AgentState):
    primary_task = state["primary_task"]
    primary_answer = state["primary_answer"]
    follow_up_question = state["follow_up_question"]
    student_response = state["current_task"]
    state["follow_up_question"] = None
    state["follow_up_task"] = student_response

    follow_up_eval_prompt = f"""
You are an AI Teaching Assistant.

Context:
Main: {primary_task}
Correct: {primary_answer}
Follow-up: {follow_up_question}
Student Answer: {student_response}

Reply to the student without revealing the answer.
""".strip()

    response = send_message_to_claude(follow_up_eval_prompt)
    print("### GRADE FOLLOW-UP RESPONSE###", response)
    state["full_response"] = response
    #state["full_reference"] = rag_support(follow_up_question)
    state["follow_up_question"] = get_last_question(response)
    return state

def grade_follow_up2(state: AgentState):
    # Same logic as grade_follow_up — call Claude
    return grade_follow_up(state)

def grade_answer(state: AgentState):
    primary_task = state["primary_task"]
    current_task = state["current_task"]
    primary_answer = state["primary_answer"]

    grading_prompt = f"""
You are an AI Teaching Assistant.

If the student's answer is correct: confirm & encourage.
If wrong: gently explain and ask a guiding question.
Do not reveal the correct answer unless the student says it.

Primary:
"{primary_task}"

Student's Answer:
"{current_task}"

Correct (internal only):
"{primary_answer}"
""".strip()

    response = send_message_to_claude(grading_prompt)
    print("###GRADE RESPONSE###", response)
    state["full_response"] = response
    state["correct_answer"] = contains_confirmation(response)
    state["follow_up_question"] = get_last_question(response)
    if state["correct_answer"]== True:
        state["attempts"]=0

    return state

def rag_support(text):
    concept_prompt = f"""
Identify main concepts to review in: "{text}"
List keywords only, comma-separated.
"""
    response = send_message_to_ollama(concept_prompt)
    retrieved_chunks = semantic_search(response)
    high_relevance_chunks = [
        chunk for chunk in retrieved_chunks if round(chunk.get("score", 0), 1) >= 0
    ]
    if not high_relevance_chunks:
        return "No relevant content found."
    context = "\n\n".join([f"Chunk {i+1}:\n{chunk['text']}" for i, chunk in enumerate(high_relevance_chunks)])
    quote_prompt = f"""
Quote only relevant lines from:
---
{context}
---
Focus: {response}
"""
    return send_message_to_claude(quote_prompt)

def get_last_question(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return None
    last = sentences[-1]
    return last if last.endswith("?") else None

def contains_confirmation(text):
    return re.search(r"\b(?:you(?:'re| are)|your answer|that is|you chose).*?\b(correct|right)\b", text, re.IGNORECASE) is not None

graph_builder = StateGraph(AgentState)
graph_builder.add_node("user_input", user_input)
graph_builder.add_node("user_input2", user_input2)
graph_builder.add_node("user_input3", user_input3)
graph_builder.add_node("user_input4", user_input4)
graph_builder.add_node("grade_follow_up", grade_follow_up)
graph_builder.add_node("grade_follow_up2", grade_follow_up2)
graph_builder.add_node("grade_answer", grade_answer)
graph_builder.add_node("follow_up", follow_up)
graph_builder.add_node("redirect", redirect)



graph_builder.add_conditional_edges(
        "user_input",
        classify_task_type,
        {True: "user_input2", False: "user_input3"}
    )
graph_builder.add_conditional_edges(
        "user_input2",
        question_type,
        {True: "redirect", False: "user_input4"}
    )
graph_builder.add_conditional_edges(
        "user_input3",
        answer_type,
        {True: "grade_follow_up", False: "grade_answer"}
    )
graph_builder.add_conditional_edges(
    "user_input4",
    follow_up_type,
    {True: "grade_follow_up2", False: "follow_up"}

)





graph_builder.set_entry_point("user_input")
checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)
config = {
        "configurable": {
            "thread_id": "user-session-1"
        }
    }
# Make sure these are imported properly

def run_question_step(user_message, session_state):
    current_primary_task = session_state.get("primary_task")
    current_primary_answer = session_state.get("primary_answer")
    current_follow_up_question = session_state.get("follow_up_question")
    current_reference = session_state.get("full_reference", None)
    current_sub_questions = session_state.get("subquestions", [])
    attempts = session_state.get("attempts", 0)

    correct_answer = False
    current_response = ""

    if current_primary_task is None:
        current_primary_task = user_message
    if current_primary_answer is None:
        current_primary_answer = ""
    if current_follow_up_question is None and len(current_sub_questions) > 0:
        current_follow_up_question = current_sub_questions.pop(0)

    initial_input = {
        "primary_task": current_primary_task,
        "primary_answer": current_primary_answer,
        "current_task": user_message,
        "follow_up_question": current_follow_up_question,
        "follow_up_task": "",
        "correct_answer": correct_answer,
        "attempts": attempts,
        "full_response": "",
        "full_reference": current_reference,
        "subquestions": current_sub_questions
    }

    for s in graph.stream(initial_input, config):
        final_state = s

    state_keys = [k for k in final_state.keys() if k != "next"]
    if not state_keys:
        raise ValueError("No valid state key found!")

    node_name = state_keys[0]
    state_data = final_state[node_name]

    current_primary_task = state_data["primary_task"]
    current_primary_answer = state_data["primary_answer"]
    current_follow_up_question = state_data["follow_up_question"]
    correct_answer = state_data["correct_answer"]
    current_response = state_data["full_response"]
    current_reference = state_data["full_reference"]

    attempts += 1

    if current_follow_up_question is None and len(current_sub_questions) > 0:
        current_follow_up_question = current_sub_questions.pop(0)


    return {
        "primary_task": current_primary_task,
        "primary_answer": current_primary_answer,
        "follow_up_question": current_follow_up_question,
        "correct_answer": correct_answer,
        "attempts": attempts,
        "current_response": current_response,
        "full_reference": current_reference,
        "subquestions": current_sub_questions,
        "full_response": current_response
    }
def run_question_step2(user_message, session_state):
    current_primary_task = session_state.get("primary_task")
    current_primary_answer = session_state.get("primary_answer")
    current_follow_up_question = session_state.get("follow_up_question")
    current_reference = session_state.get("full_reference", None)
    current_sub_questions = session_state.get("subquestions", [])
    attempts = session_state.get("attempts", 0)

    correct_answer = False
    current_response = ""

    if current_primary_task is None:
        current_primary_task = user_message
    if current_primary_answer is None:
        current_primary_answer = ""
    if current_follow_up_question is None and len(current_sub_questions) > 0:
        current_follow_up_question = current_sub_questions.pop(0)

    initial_input = {
        "primary_task": current_primary_task,
        "primary_answer": current_primary_answer,
        "current_task": user_message,
        "follow_up_question": current_follow_up_question,
        "follow_up_task": "",
        "correct_answer": correct_answer,
        "attempts": attempts,
        "full_response": "",
        "full_reference": current_reference,
        "subquestions": current_sub_questions
    }
    session_state = ""
