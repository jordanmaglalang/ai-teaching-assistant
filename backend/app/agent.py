from dotenv import load_dotenv
import os
# Load environment variables
_ = load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
from extract_content import get_doc_content, get_text_from_pdf, doc_path, pdf_path
from vector_db import main, initialize_vector_db, split_into_chunks, semantic_search, pc, index_name, query
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, state
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict


model = ChatOpenAI()

doc_text = get_text_from_pdf(pdf_path)
chunks = split_into_chunks(doc_text)
print(f"Split text into {len(chunks)} chunks.")
records = []
for i, chunk in enumerate(chunks):
    records.append({
        "_id": f"resume-chunk-{i}",
        "chunk_text": chunk,
        "category": "resume"
    })
initialize_vector_db(index_name)

index = pc.Index(index_name)
print("Upserting records...")
index.upsert_records("ns1", records)
print(f"Upserted {len(records)} chunks into namespace 'ns1'.")


class AgentState(TypedDict):
    primary_task: str
    current_task: str
    relevancy: bool
    new_primary: bool

def classify_task_type(state:AgentState):




    classification_prompt = f"""
    You are an assistant that determines whether a student is continuing their current topic or switching to a new one.

    Here’s how to classify:

    - If the student's new question is closely related to the original question (e.g., it's a clarification, expansion, or detail about the same topic), respond with **"False"** — it's a follow-up.
    - If the new question changes to a clearly unrelated topic, respond with **"True"** — it's a new topic.

    Examples:
    - Original: "What is a for loop?"  
    New: "How does iteration work?" → False
    - Original: "What is a for loop?"  
    New: "What is a binary tree?" → True
    - Original: "What is recursion?"  
    New: "Is it used in sorting?" → False
    - Original: "What is an EAX register?"  
    New: "Is it in the CPU?" → False

    Now classify this:

    Original question (primary task):  
    "{state['primary_task']}"

    New question (current task):  
    "{state['current_task']}"

    Respond with only "True" or "False".
    """

    print("CLASSIFICATION PROMPT")
    print(classification_prompt)
    response = model.invoke([SystemMessage(classification_prompt)])
    state['new_primary'] = bool(response.content)
    print(state['new_primary'])
    if state['new_primary'] == True:
        state['primary_task'] = state['current_task']
       
    return state


def chat(state: AgentState):
    # Perform semantic search with the current question
    current_query = state["current_task"]
    top_results = semantic_search(current_query)

    # Format chunk_context_and_scores string for the prompt (assuming top_results is a list of dicts)
    

    TA_PROMPT = f"""You are an AI Teaching Assistant guiding a student to learn through questioning (Socratic method).

Your job is to help the student reach the answer to their *primary question*, by evaluating and responding to their *current input* (which might be a guess, a reasoning attempt, or a follow-up question).

You have access to a set of context snippets ("chunks") related to the student's primary question, each with a relevance score.

Use these rules to handle chunk context:
- For chunks with score ≥ 0.5: rely confidently on their content to guide your questions and explanations.
- For chunks with scores between 0.1 and 0.5: use their content cautiously, combining it with your own reasoning.
- For chunks with score < 0.1: ignore the chunk content entirely.

You are also provided with two fields:
- `primary_task`: the student's original question or problem.
- `current_task`: the student's most recent message.

Now, behave according to this decision logic:

---

1. **If the current_task is simply another question or an attempt to make progress toward solving the primary_task:**
    - Ask a helpful **follow-up question** related to the primary_task, based on their current_task.
    - Help them think more deeply or correct their line of reasoning.
    - Encourage reflection and lead them forward without giving the final answer.

2. **If the current_task is an attempted answer or explanation for the primary_task:**
    - First, determine if the student’s answer is **correct**.
        - ✅ If **correct**: 
            - Congratulate the student warmly.
            - Provide a clear explanation of **why** their answer is right, referencing the chunks if helpful.
        - ❌ If **incorrect**:
            - Gently correct their misunderstanding without giving the full answer.
            - Ask a guiding question that nudges them in the right direction.
            - Reference helpful chunk content if appropriate.

3. **If it's unclear whether the input is a follow-up or an answer:**
    - Assume it’s an exploratory step and treat it like a follow-up.
    - Use probing questions to encourage deeper thinking or clarification.

---

Always avoid direct answers before the student has interacted with the system for at least 5 questions (unless their answer is correct). Encourage learning, not just answering.

Be patient, respectful, and positive.

---

Here is the student's primary question:

{state['primary_task']}

Here is their most recent message:

{state['current_task']}

Here is the relevant chunk context and their scores:

{top_results}

Your response:

"""

    messages = [
        SystemMessage(TA_PROMPT)
    ]
    response = model.invoke(messages)
    print("##TA RESPONSE##", response.content)
    return state

graph_builder = StateGraph(AgentState)
graph_builder.add_node("start", classify_task_type)
graph_builder.add_node("chatbot", chat)
graph_builder.add_edge("start", "chatbot")
graph_builder.set_entry_point("start")

checkpointer = InMemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)
config = {
    "configurable": {
        "thread_id": "user-session-1"
    }
}

current_primary_task = None
while True:
    user_input = input("Ask your question (or type 'exit' to quit): ")
    if user_input.strip().lower() == "exit":
        print("Goodbye!")
        break

    if current_primary_task is None:
        current_primary_task = user_input

    initial_input = {
        "current_task": user_input,
        "primary_task": current_primary_task
    }
    for s in graph.stream(initial_input):
        # This yields intermediate states/events, print only final if you want
        print("Stream event:", s)
