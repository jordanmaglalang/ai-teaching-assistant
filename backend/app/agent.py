from dotenv import load_dotenv
import os
# Load environment variables
_ = load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
from extract_content import get_text_from_pdf, doc_path, pdf_path
from vector_db import initialize_vector_db, split_into_chunks, semantic_search, pc, index_name, query
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, state
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict
from langchain.agents import initialize_agent, AgentType
from tools import retrieve_relevant_chunks
import re


model = ChatOpenAI()
tools = [retrieve_relevant_chunks]

model_with_tools = initialize_agent(
    tools=tools,
    llm=model,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)



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
    first_question: bool
    primary_task: str
    current_task: str
    primary_answer: str
    attempts: int
    follow_up_question:str
    follow_up_task: str
    




def user_input(state:AgentState):
    return state
def user_input2(state:AgentState):
    return state
def user_input3(state:AgentState):
    return state
def user_input4(state:AgentState):
    return state
def classify_task_type(state: AgentState):
    current_task = state["current_task"]
    
    

    classification_prompt = f"""
    You are an AI assistant classifying student input.

    Classify the student's message as one of:

    - question: If the message is asking for information, clarification, or help — including multiple-choice questions (with options like "a)", "b)", etc.) or uncertain responses like "I don't know", "No idea", or "Not sure".
    - attempted_answer: If the message is trying to provide an explanation, opinion, guess, or partial answer — even if phrased as a question (e.g., "Could it be...", "Is it...").
    
    **Student Message:**  
    "{current_task}"

    Examples:

    1. "What is a function?" → question  
    2. "I don't know." → question  
    3. "No idea" → question  
    4. "Could it be photosynthesis?" → attempted_answer  
    5. "Isn't an ion a charged atom?" → attempted_answer  
    6. "A variable stores data." → attempted_answer  
    7. "I think it's related to energy." → attempted_answer  
    8. "How does the loop stop?" → question  
    9. "What is the major difference between A and B? a) one is hydrophobic b) one is polar" → question  
    10. "What is the best option? a) dog b) cat c) fish" → question

    Respond with only one of:
    - question
    - attempted_answer
    """.strip()





    

    response = model.invoke([SystemMessage(classification_prompt)])
    response_text = str(response.content).strip().lower().strip(".")

    print("##CLASSIFY TASK TYPE##", response_text)
    print("STATE OF THE PRIMARY QUESTION IS ", state['primary_task'])
    
    is_question = response_text == "question"

   
    return is_question 


def question_type(state:AgentState):
    primary_task = state['primary_task']   
    current_task = state['current_task']
    response_id = f"""
You are an AI Teaching Assistant.

Determine whether the student's message is:

- follow up question: A clarifying or related question that continues the discussion of the current main question.
- new main question: A new, unrelated question that introduces a different topic, even if it is within the same subject. Even if both questions are from the same subject area (e.g., biology, chemistry, programming), a question should only be considered a **follow-up** if it builds on the *same concept or explanation*.  
If the student's message asks about a **different concept**, **definition**, **classification**, or **dimension** — even if related — it should be classified as a **new main question**.


**Current Main Question:**  
"{primary_task}"

**Student's Message:**  
"{current_task}"

Classify the message with just one of:

- follow up question
- new main question


Examples:

1. Primary: "What is recursion?"  
   Student: "Is that like a function calling itself?" → follow up question

2. Primary: "What is recursion?"  
   Student: "How do while loops work?" → new main question

3. Primary: "What are arrays?"  
   Student: "What about linked lists?" → new main question 

4. Primary: "How does a for loop work?"  
   Student: "What happens if I put a break inside it?" → follow up question

5. Primary: "What is a ketose?"  
   Student: "What is a pentose?" → new main question  
   *(The student switches from functional group type to carbon number — a different classification dimension.)*

""".strip()
    print("QUESTION TYPE PROMPT , ", response_id )
    response = model.invoke([SystemMessage(response_id)])
    response_text = str(response.content).strip().lower().strip(".")
    print("##RESULT OF QUESTION TYPE IS## ", response_text)
    answer = response_text == "new main question"
    print("ANSWER IS ", answer, " ATTEMPTS IS, ", state['attempts']==0)
    
    return answer or state['attempts']==0
def generate_answer(state: AgentState):
    state['primary_task'] = state['current_task']
    print("CURRENT TASK (genANs) IS ", state["current_task"])

    question = state["primary_task"]
    print("QUESTION IS ,", question)
   
    answer_prompt = f"""
You are a highly knowledgeable teaching assistant.

The student has asked a question. It may or may not include multiple-choice options.

Your task is to:

1. Determine whether the question includes multiple-choice options.
2. If it does:
   - Identify the correct option (e.g., A, B, C, D).
   - State the correct choice (e.g., "The correct answer is A").
   - Provide a brief explanation of why that option is correct.
   - Optionally, explain why the other options are incorrect.
3. If it does **not** include multiple-choice options:
   - Provide a direct, accurate answer in your own words.
   - Keep your explanation clear and concise.

---

Student Question:
"{question}"

Begin your response accordingly.
""".strip()



    response = model.invoke([SystemMessage(answer_prompt)])
    answer = response.content.strip()
    state["primary_answer"] = answer
    print("GENERATE ANSWER PROMPT , ", answer_prompt)
    print("📌 Stored correct answer:", answer)
    print("GENERATE AND AFTER THAT, THE ASTATE OF PRIMARY TASK IS ", state['primary_task'])
  
    
   
    return state

def first_hint(state:AgentState):
    answer = state["primary_answer"]
    question = state['primary_task']
    print("FIRST HINT TO ANSWER ", answer)
    print("FIRST HINT TO QUESTION ", question)
    followup_prompt = f"""
You are a helpful and knowledgeable teaching assistant.

The student asked the following main question:
"{question}"

You already provided the following answer:
"{answer}"

If the question is a multiple-choice question:
- Do NOT state or confirm the correct answer.
- Do NOT say whether the student is correct or incorrect.
- Instead, guide the student toward the correct choice by:
  - Highlighting relevant clues.
  - Quoting a relevant sentence or phrase from course materials if helpful.
  - Asking reflective or guiding questions.
  - Clarifying terms or concepts without solving the question for them.

If the question is **not** multiple-choice:
- Provide a clear, accurate answer in your own words.
- Quote course material if it helps reinforce or validate your explanation.

You have access to a tool that retrieves relevant chunks from the course materials. Use it when quoting a short, specific part of a chunk can help support your hint or explanation.

Always focus on guiding the student toward understanding — not simply giving away the answer.
""".strip()


    response = model_with_tools.invoke([SystemMessage(followup_prompt)])
    print("##HINT RESPONSE ##",response["output"])
    rag_support(str(response["output"]))
    state['follow_up_question']= get_last_question(response["output"])
    return state
def follow_up_type(state:AgentState):
    
    if not state['follow_up_question']:
        print("FOLLOW_UP_TYPE IS ", state["follow_up_question"])
        return False
    
    print("FOLLOW_UP_TYPE IS## ", state["follow_up_question"])
    return True
def grade_follow_up2(state:AgentState):
    primary_task = state["primary_task"]
    follow_up_question = state["follow_up_question"]
    state['follow_up_task'] = state["current_task"]
    student_response = state["follow_up_task"]
    state["follow_up_question"] = None
    follow_up_eval_prompt = f"""
    You are an AI Teaching Assistant guiding a student through a concept.

    A follow-up question was created to help the student rethink or clarify their misunderstanding of the original main question.

    Here’s the context:

    🧠 Main Question:
    {primary_task}

    📌 Follow-Up Question:
    {follow_up_question}

    ✏️ Your Response:
    {student_response}

    ---

    Now respond directly to the student.

    - If their follow-up answer is **correct**:
    - Confirm their answer.
    - Briefly explain why it’s right.
    - Help them connect this back to the **main question** to reinforce learning.

    - If their answer is **partially correct**:
    - Acknowledge what's right.
    - Clarify what’s missing.
    - Offer a hint or guidance.

    - If their answer is **incorrect**:
    - Gently explain that it's not quite right.
    - Offer a helpful hint or ask a guiding question.

    Keep it supportive and clear, as if you're speaking directly to the student.
    """.strip()


    print("##PROMPT IS FOR RESPONSE TO FOLLOW UP QUESTION##", follow_up_eval_prompt)
    response = model.invoke([SystemMessage(follow_up_eval_prompt)])
    print("##FOLLOW UP EVAL##", response.content)
    state["follow_up_question"] = get_last_question(response.content)
    return state

def follow_up(state:AgentState):
    primary_task = state['primary_task']
    current_task = state['current_task']
    primary_answer = state['primary_answer']
    guide= f"""
You are an AI Teaching Assistant using the Socratic method.

The main question is:  
"{primary_task}"

The student has asked a follow-up question:  
"{current_task}"

Generate a meaningful, guiding question that helps the student think deeper and move closer to the answer.

Do NOT give the answer.
"""
    response = model.invoke([SystemMessage(guide)])
    print("###FEEDBACK RESPONSE###", response.content)
    state["follow_up_question"] = get_last_question(response.content)
    print("GET LAST QUESTION TO THE FOLLOW UP QUESTION'S RESPONSE,", state["follow_up_question"])
    return state

def answer_type(state:AgentState):
    if not state['follow_up_question']:
        print("FALSE FOR ANSWER TYPE")
        return False
    
    print("TRUE FOR ANSWER TYPE")
    return True
def grade_follow_up(state:AgentState):
    state["follow_up_task"] = state["current_task"]
    student_response = state["follow_up_task"]
    follow_up_question = state["follow_up_question"]
    primary_task = state["primary_task"]
    state["follow_up_question"] = None
    print("##MY FOLLOW UP TASK## ", student_response)
    follow_up_eval_prompt = f"""
    You are an AI Teaching Assistant guiding a student through a concept.

    A follow-up question was created to help the student rethink or clarify their misunderstanding of the original main question.

    Here’s the context:

    🧠 Main Question:
    {primary_task}

    📌 Follow-Up Question:
    {follow_up_question}

    ✏️ Your Response:
    {student_response}

    ---

    Now respond directly to the student.

    - If their follow-up answer is **correct**:
    - Confirm their answer.
    - Briefly explain why it’s right.
    - Help them connect this back to the **main question** to reinforce learning.

    - If their answer is **partially correct**:
    - Acknowledge what's right.
    - Clarify what’s missing.
    - Offer a hint or guidance.

    - If their answer is **incorrect**:
    - Gently explain that it's not quite right.
    - Offer a helpful hint or ask a guiding question.

    Keep it supportive and clear, as if you're speaking directly to the student.
    """.strip()


    print("##PROMPT IS##", follow_up_eval_prompt)
    response = model.invoke([SystemMessage(follow_up_eval_prompt)])
    print("##FOLLOW UP EVAL##", response.content)
    state['follow_up_question']= get_last_question(response.content)


    return state

def grade_answer(state:AgentState):
    primary_task = state['primary_task']
    current_task = state['current_task']
    primary_answer = state['primary_answer']
    print("GRADE ANSWER FOR QUESTION ", state['primary_answer'])

    

    
    
    grading_prompt = f"""
    You are an AI Teaching Assistant.

    Primary question:  
    "{primary_task}"

    Student's attempted answer:  
    "{current_task}"

    Correct answer (for internal comparison only — do NOT reveal to the student):  
    "{primary_answer}"

    Your task is to evaluate whether the student's answer is semantically correct (has the same core meaning as the correct answer).

    Instructions:

    - If the student's answer is correct:
    - Congratulate the student.
    - Briefly explain why their answer is correct using supporting reasoning or concepts.

    - If the student's answer is incorrect:
    - DO NOT say or hint at the correct answer.
    - DO NOT state or explain what the correct answer is.
    - DO NOT say things like "The correct answer is..." or "The correct linkage is..." or any sentence that reveals or paraphrases the correct answer in any way.
    - DO NOT reference, rephrase, or define the correct answer or its key terms.
    - Only explain why the student's answer is **incorrect** based on conceptual misunderstanding or confusion.
    - End by asking a helpful guiding question to encourage the student to think further.

    ⚠️ ABSOLUTELY DO NOT reveal or describe the correct answer — this includes its letter, terminology, or paraphrased explanation — unless the student's answer is correct.

    Respond only with your feedback to the student.
    """.strip()


    response = model.invoke([SystemMessage(grading_prompt)])
    print("###GRADE RESPONSE###", response.content)
    

    state["follow_up_question"] = get_last_question(response.content)
    print("##FOLLOW UP TASK##", state["follow_up_question"])
    return state
def rag_support(text):
    print("RECEIVED RAG SUPPORT")
    
   
    # Step 1: Use model to identify key concepts to review based on feedback
    concept_extraction_prompt = f"""
    You are an AI teaching assistant.

    A student has received the following feedback on their answer:
    "{text}"

    Your task:
    - Identify the **main concept(s)** the student should review or focus on to improve.
    - Be concise and specific (e.g. "alpha-1,6 glycosidic linkages", "role of enzymes in digestion").
    - List only the keywords or short phrases (no full sentences).

    Output a comma-separated list of key concepts.
    """.strip()

    response = model.invoke(concept_extraction_prompt)
    print("CONCEPTS ARE ", response.content)


    if not response:
        return "No key concepts found."

    # Step 2: Use your retrieval tool (vector search) to get top relevant chunks
    retrieved_chunks = semantic_search(response.content)
    print("RETRIEVED CHUNKS ", retrieved_chunks)
      # Step 3: Filter for relevance score > 0.5
    high_relevance_chunks = [
        chunk for chunk in retrieved_chunks if  round(chunk.get("score", 0), 1) >= 0.
    ]
    
    if not high_relevance_chunks:
        print("No relevant content found.")
        return "No relevant content found."

    # Step 4: Build context from filtered chunks
    context = "\n\n".join([
        f"Chunk {i+1}:\n{chunk['text']}" for i, chunk in enumerate(high_relevance_chunks)
    ])
    print("##CONTEXT  , ", context)
    
    # Step 5: Quote only the directly relevant support from those chunks
    quote_prompt = f"""
    
    You are an AI assistant that helps students reinforce feedback using their course materials.

    Focus area(s): {high_relevance_chunks}

    Below are excerpts from the course materials:
    ---
    {context}
    ---

    Your task:
    - Quote only the lines or phrases that directly relate to the focus areas above.
    - Use **verbatim** quotes only — do not paraphrase.
    - Do not explain or summarize.
    - If none of the excerpts clearly match the focus areas, respond with: "No relevant content found."

    Begin quoting.
    """.strip()



    response2 = model.invoke(quote_prompt)
    print("QUOTES FOUND ", response2.content)
    

    return True


def get_last_question(text):
    print("###received get last question###")
    # Split the text into sentences using punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Get the last sentence
    if not sentences:
        return None

    last_sentence = sentences[-1]

    # Check if the last sentence ends with a question mark
    if last_sentence.endswith('?'):
        print("###THE QUESTION TO STORE IS###", last_sentence.strip())
        return last_sentence.strip()
    
    return None



graph_builder = StateGraph(AgentState)
graph_builder.add_node("user_input", user_input)
graph_builder.add_node("generate_answer", generate_answer)
graph_builder.add_node("user_input2", user_input2)
graph_builder.add_node("grade_answer", grade_answer)
graph_builder.add_node("follow_up", follow_up)
graph_builder.add_node("hint", first_hint)
graph_builder.add_node("user_input3", user_input3)
graph_builder.add_node("grade_follow_up", grade_follow_up)
graph_builder.add_node("user_input4", user_input4)
graph_builder.add_node("grade_follow_up2", grade_follow_up2)
graph_builder.add_edge("generate_answer", "hint")

graph_builder.add_conditional_edges(
        "user_input",
        classify_task_type,
        {True: "user_input2", False: "user_input3"}
    )
graph_builder.add_conditional_edges(
        "user_input2",
        question_type,
        {True: "generate_answer", False: "user_input4"}
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

current_primary_task = None
current_primary_answer = None
current_follow_up_question = None
attempts = 0
while True:
    
   
    user_input = input("Ask your question (or type 'exit' to quit): ")
    if user_input.strip().lower() == "exit":
        print("Goodbye!")
        break
    
    if current_primary_task is None:
        current_primary_task = user_input
    if current_primary_answer is None:
        current_primary_answer = ""
    initial_input = {
        "attempts": attempts,
        "current_task": user_input,
        "primary_task": current_primary_task,
        "primary_answer": current_primary_answer,
        "follow_up_question": current_follow_up_question
        
    }
   
    for s in graph.stream(initial_input,config):
        # This yields intermediate states/events, print only final if you want
        final_state = s 
    
    print("Final state keys:", final_state.keys())
    print("Full final state:", final_state)
    if "hint" in final_state:
        current_primary_task = final_state["hint"]["primary_task"]
        current_primary_answer = final_state["hint"]["primary_answer"]
        print("###PRIMARY TASK IS ####", current_primary_task)
    if "grade_answer" in final_state:
        
        current_primary_task = final_state["grade_answer"]["primary_task"]
        current_primary_answer = final_state["grade_answer"]["primary_answer"]
        current_follow_up_question = final_state["grade_answer"]["follow_up_question"]
        print("##GRADE ANSWER## ", current_primary_task)
    if "grade_follow_up" in final_state:
        current_follow_up_question = final_state["grade_follow_up"]["follow_up_question"]
        print("##CURRENT FOLLOW UP QUESTION IS##", current_follow_up_question)
    if "follow_up" in final_state:
        current_follow_up_question = final_state["follow_up"]["follow_up_question"]
    attempts +=1