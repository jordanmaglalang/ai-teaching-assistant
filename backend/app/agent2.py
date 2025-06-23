from dotenv import load_dotenv
import os
# Load environment variables
_ = load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
from extract_content import get_text_from_ppt, pptx_path
from vector_db import initialize_vector_db, split_into_chunks, semantic_search, pc, index_name, query
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, state
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict
from langchain.agents import initialize_agent, AgentType
from tools import retrieve_relevant_chunks, create_question
import re


model = ChatOpenAI()
tools = [retrieve_relevant_chunks, create_question]

model_with_tools = initialize_agent(
    tools=tools,
    llm=model,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    
)



doc_text = get_text_from_ppt(pptx_path)
chunks = split_into_chunks(pptx_path)
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
    primary_answer: str
    attempts: int
    follow_up_question:str
    follow_up_task: str
    correct_answer: bool
    




def user_input(state:AgentState):
    if state["attempts"] == 0:
       state["primary_answer"] =  generate_answer(state["current_task"])
       print("#CURRENT PRIMARY ANSWER# ", state["primary_answer"])
    
    return state
def user_input2(state:AgentState):
    return state
def user_input3(state:AgentState):
    return state
def user_input4(state:AgentState):
    return state
def generate_answer(current_task):
    question_type_prompt =f"""
You are an AI assistant helping classify student questions.

Your task is to determine whether the following question is:

- A multiple-choice question (MCQ), which includes answer options like A, B, C, D
- A free response question (FRQ), which does not include any answer choices

Only respond with one of the following labels:

- "MCQ"
- "FRQ"

Question:
"{current_task}"
""".strip()
    
    mcq_prompt = f"""
    You are a highly knowledgeable teaching assistant.

    The following student question is a **multiple-choice question**.

    Your task is to:
    1. Identify the correct answer choice (A, B, C, D, etc.)
    2. State the correct choice clearly (e.g., "The correct answer is A")
    

    Question:
    "{current_task}"
""".strip()
    frq_prompt = f"""
You are a highly knowledgeable teaching assistant.

The following student question is a **free response question**, meaning it does not contain multiple-choice options.

Your task is to:
1. Provide a direct, accurate answer in your own words
2. Keep your explanation clear and concise
3. Use simple language appropriate for a high school or college student

Question:
"{current_task}"
""".strip()
    response1 = model.invoke([SystemMessage(question_type_prompt)])
    q_type = response1.content.strip().lower()
    print("Q TYPE IS ", q_type)
    

    if q_type == "frq":
        response2 = model.invoke([SystemMessage(frq_prompt)])
    else:
        response2 = model.invoke([SystemMessage(mcq_prompt)])
    
    


    
   
    
    print("📌 Stored correct answer:", response2.content.strip())

    
    
   
    return response2.content.strip()


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
    if state["follow_up_question"]:
        follow_up = state["follow_up_question"]
    else:
        follow_up = None
    response_id = f"""
You are an AI Teaching Assistant.

Determine whether the student's message is:

- **related**: A clarifying or follow-up message that continues the discussion of the current main question. It builds on the *same concept, explanation, or idea* — even if the message is vague (e.g., “I don’t know,” “teach me,” “explain more,” or “can you help me with this?”). These count as related if the student is still seeking to learn about the same topic.

- **unrelated**: A message that introduces a *different concept, definition, classification, or topic*, even if it's within the same subject area. If the student's message changes the focus away from the original main question, it should be considered unrelated.

Your task is to classify the student's message as either **related** or **unrelated**, based only on whether it maintains focus on the original main question or follow up question.

---

**Current Main Question:**  
"{primary_task}"

**Follow up Question:**

"{follow_up}
**Student's Message:**  
"{current_task}"

Classify the message with just one of:

- related  
- unrelated

---

### Examples:

1. Primary: "What is recursion?"  
   Student: "Is that like a function calling itself?" → **related**

2. Primary: "What is recursion?"  
   Student: "How do while loops work?" → **unrelated**

3. Primary: "What are arrays?"  
   Student: "What about linked lists?" → **unrelated**  
   *(This changes the data structure being discussed.)*

4. Primary: "How does a for loop work?"  
   Student: "What happens if I put a break inside it?" → **related**

5. Primary: "What is a ketose?"  
   Student: "What is a pentose?" → **unrelated**  
   *(This shifts from type of sugar to carbon count — a different classification.)*

6. Primary: "Explain the concept of big and little endian"  
   Student: "I don’t know. Teach me." → **related**

7. Primary: "What is polymorphism in OOP?"  
   Student: "Can you explain it again but simpler?" → **related**

8. Primary: "How does the stack work in function calls?"  
   Student: "How do heaps work?" → **unrelated**


""".strip()


    print("QUESTION TYPE PROMPT , ", response_id )
    response = model.invoke([SystemMessage(response_id)])
    response_text = str(response.content).strip().lower().strip(".")
    print("##RESULT OF QUESTION TYPE IS## ", response_text)
    answer = response_text == "unrelated"
    #print("ANSWER IS ", answer, " ATTEMPTS IS, ", state['attempts']==0)
    
    return answer 


def redirect(state:AgentState):
    primary_task = state["primary_task"]
    current_task = state["current_task"]
    redirect_prompt= f"""
You've already identified the student's message as unrelated to the original main question.

Now, respond directly to the student using second person language (e.g., "you," "your question," "let's").

Your response should:

1. Acknowledge the interest or curiosity behind their question.
2. If their question is within the same subject area, briefly suggest how it might relate — but don’t explain the unrelated topic.
3. Guide them back to the original main question by asking a thoughtful, open-ended question that helps refocus their attention.

Keep your tone encouraging, conversational, and focused on helping them understand the original topic.

---

**Original Main Question:**  
"{primary_task}"

**Unrelated Student Message:**  
"{current_task}"

Write a short, second-person response that:
- Acknowledges their curiosity,
- Optionally bridges back to the original topic,
- Ends with a guiding question to bring them back on track.
"""


    response = model.invoke([SystemMessage(redirect_prompt)])
    print("##REDIRECT## ", response.content)

    return state

def follow_up_type(state:AgentState):
    
    if not state['follow_up_question']:
        print("FOLLOW_UP_TYPE IS ", state["follow_up_question"])
        return False
    
    print("FOLLOW_UP_TYPE IS## ", state["follow_up_question"])
    return True
def grade_follow_up2(state:AgentState):
    primary_task = state["primary_task"]
    primary_answer = state["primary_answer"]
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

    Answer to Main Question
    {primary_answer}

    📌 Follow-Up Question:
    {follow_up_question}

    ✏️ Student Response:
    {student_response}

    ---

    Now respond directly to the student. Do NOT give the answer or mention the answer in guiding the explanation.

    

    
    
    """.strip()


    print("##PROMPT IS FOR RESPONSE TO FOLLOW UP QUESTION##", follow_up_eval_prompt)
    response = model.invoke([SystemMessage(follow_up_eval_prompt)])

    print("##FOLLOW UP EVAL##", response.content)
    rag_support(follow_up_question)
    state["follow_up_question"] = get_last_question(response.content)
    return state

def follow_up(state:AgentState):
    primary_task = state['primary_task']
    current_task = state['current_task']
    primary_answer = state['primary_answer']
    guide = f"""
You are an AI Teaching Assistant who uses the Socratic method to help students discover correct answers on their own.

You are assisting a student with the following multiple-choice question:

🧠 Main Question:  
"{primary_task}"

✅ Correct Answer:  
{primary_answer}

✏️ The student’s follow-up message or confusion is:  
"{current_task}"

Your task is to craft a guiding response with a question that makes the student to reflect and think critically — without revealing the correct answer directly or using any keywords/phrases from it.




"""

    response = model.invoke([SystemMessage(guide)])
    print("###FEEDBACK RESPONSE###", response.content)
    state["follow_up_question"] = get_last_question(response.content)
    print("GET LAST QUESTION TO THE FOLLOW UP QUESTION'S RESPONSE,", state["follow_up_question"])
    return state

def answer_type(state:AgentState):
    print("#ANSWER TYPE#")
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
    primary_answer = state["primary_answer"]
    state["follow_up_question"] = None
    print("##MY FOLLOW UP TASK## ", student_response)
    follow_up_eval_prompt = f"""
    You are an AI Teaching Assistant guiding a student through a concept.

    A follow-up question was created to help the student rethink or clarify their misunderstanding of the original main question.

    Here’s the context:

    🧠 Main Question:
    {primary_task}

    Answer to Main Question
    {primary_answer}

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

    -If their answer is none of the 3 options, respond to them with accordance to their request, in the context of the follow-up question, the answer to the main question, and the main question, without revealing the answer.


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
You are an AI Teaching Assistant evaluating a student's answer to a multiple-choice question.

🧠 Primary question:
"{primary_task}"

✏️ Student's attempted answer:
"{current_task}"

✅ Correct answer (for internal reference only — do NOT reveal this unless the student is correct):
"{primary_answer}"

---

Your task:

- If the student's answer is **correct or nearly correct** (e.g., "A", "photsynthesis", or even "is it photosynthesis?"):
    - Confirm they’re right in a friendly tone.
    - Use second person (e.g., “You’re right,” “That’s correct”).
    - Encourage them to explain *why* they think it’s correct to deepen their understanding. 

- If the student's answer is **incorrect** or mentions the wrong option:
    - DO NOT reveal or describe the correct answer.
    - Use second person to explain why their answer isn’t correct based only on what they wrote in a respectful and constructive way.
    - Ask a guiding follow-up question to help them think more critically.

Examples of correct responses to accept:
- “A”
- “Option A”
- “32”
- “so it’s 32?”
- “I think it’s A because...”


Avoid repeating the original answer or giving away clues unless they’ve already said it.

Respond only with your feedback to the student, in second person.
""".strip()





    response = model_with_tools.invoke([SystemMessage(grading_prompt)])
    print("##RESPONSE GRADE FOR ANSWER## ", grading_prompt)
    print("###GRADE RESPONSE###", response["output"])
    state["follow_up_question"] = get_last_question(response["output"])
    print(contains_confirmation(response["output"]))
    state["correct_answer"]=contains_confirmation(response["output"])

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

def contains_confirmation(text):
    pattern = r"\b(?:you(?:'re| are)|your answer|that is|you chose).*?\b(correct|right)\b"
    return re.search(pattern, text, re.IGNORECASE) is not None

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

current_primary_task = None
current_primary_answer = None
current_follow_up_question = None
correct_answer = False
attempts = 0
while correct_answer == False:
    print("beginning state of correct answer ", correct_answer)
   
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
    if "redirect" in final_state:
        current_primary_task = final_state["redirect"]["primary_task"]
        current_primary_answer = final_state["redirect"]["primary_answer"]
        current_follow_up_question = final_state["redirect"]["follow_up_question"]
        print("###PRIMARY TASK IS ####", current_primary_task)
    if "grade_answer" in final_state:
        
        current_primary_task = final_state["grade_answer"]["primary_task"]
        current_primary_answer = final_state["grade_answer"]["primary_answer"]
        current_follow_up_question = final_state["grade_answer"]["follow_up_question"]
        correct_answer = final_state["grade_answer"]["correct_answer"]
        print("STATE OF CURRENT ANSWER ", correct_answer)
        print("##GRADE ANSWER## ", current_primary_task)
    if "grade_follow_up" in final_state:
        current_primary_task = final_state["grade_follow_up"]["primary_task"]
        current_primary_answer = final_state["grade_follow_up"]["primary_answer"]
        current_follow_up_question = final_state["grade_follow_up"]["follow_up_question"]

        print("##CURRENT FOLLOW UP QUESTION IS##", current_follow_up_question)
    if "grade_follow_up2" in final_state:
        current_primary_task = final_state["grade_follow_up2"]["primary_task"]
        current_primary_answer = final_state["grade_follow_up2"]["primary_answer"]
        current_follow_up_question = final_state["grade_follow_up2"]["follow_up_question"]

        print("##CURRENT FOLLOW UP QUESTION IS##", current_follow_up_question)
    if "follow_up" in final_state:
        current_primary_task = final_state["follow_up"]["primary_task"]
        current_primary_answer = final_state["follow_up"]["primary_answer"]
        current_follow_up_question = final_state["follow_up"]["follow_up_question"]
    attempts +=1
