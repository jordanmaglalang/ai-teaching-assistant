from dotenv import load_dotenv
import os
# Load environment variables
_ = load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
from extract_content import get_doc_content, get_text_from_pdf, doc_path, pdf_path
from vector_db import main, initialize_vector_db, split_into_chunks, semantic_search,pc, index_name, query

from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
import langchain
from typing import TypedDict, List
from bson import ObjectId
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph


model = ChatOpenAI()
class AgentState(TypedDict):
    task: str
    relevancy: bool
    
    conversation_history: List[str]
    notes_history: List[str]
    response: str

chunk_context_and_scores=""
user_question=" "


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

    # Get index handle
index = pc.Index(index_name)
print("Upserting records...")
index.upsert_records("ns1", records)
print(f"Upserted {len(records)} chunks into namespace 'ns1'.")

# Perform semantic search
top_results = semantic_search(query)
#print(top_results)

user_question = query
chunk_context_and_scores = top_results

TA_PROMPT=f"""You are an AI Teaching Assistant guiding a student to learn through questioning (Socratic method). 

You have access to a set of context snippets ("chunks") related to the student's question, each with a relevance score.

Use these rules to handle chunk context:

- For chunks with score ≥ 0.5: rely confidently on their content to guide your questions and explanations.
- For chunks with scores between 0.1 and 0.5: use their content cautiously, combining it with your own reasoning to help the student.
- For chunks with score < 0.1: ignore the chunk content; it is not relevant.

Always encourage the student to think and reason for themselves instead of giving direct answers.

Do NOT provide the final answer before the student has asked 5 questions. Instead, ask open-ended, guiding questions that help the student progress.

When you respond, you may reference the chunk content only when it is useful and relevant.

Be patient, respectful, and encouraging.

---

Here is the relevant chunk context and their scores:

{chunk_context_and_scores}

The student’s question is:

{user_question}

Your response:

"""
print(TA_PROMPT)



