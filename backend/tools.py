from langchain_community.tools import tool
from vector_db import semantic_search
from langchain_openai import ChatOpenAI
import os

# Only initialize if API key is available
GPT_API_KEY = os.getenv("OPENAI_API_KEY")
model2 = ChatOpenAI() if GPT_API_KEY else None
@tool
def retrieve_relevant_chunks(query:str)->str:
    """
    Retrieve the top 3 relevant chunks from Pinecone given a semantic query.
    """
    print("##RUN TOOL 1##")
    return semantic_search(query)
@tool(description="Generate a multiple-choice question based on a topic and an explained concept.")
def create_question(topic: str, concept_explained: str) -> str:
    prompt = f"""
    You are a Multiple-Choice Question Generator for an AI Teaching Assistant.

    Your task is to write **one** conceptual multiple-choice question (MCQ) with 4 options (A, B, C, D), related to the following topic:

    Topic: {topic}

    Concept explained: {concept_explained}

    Guidelines:
    - Make sure the question checks the student’s understanding of the concept without copying any sentence from the original answer.
    - Only one answer should be correct.
    - Do NOT include an answer key in your output.
    - Use neutral, academic language.
    - Provide only the question and its 4 options.

    Format:
    Question: <text>  
    A. <option>  
    B. <option>  
    C. <option>  
    D. <option>
    """.strip()

    # Now send to GPT
    if model2:
        response = model2.invoke(prompt)
        print("##CREATE QUESTION## ", response.content)
        answer_extraction_prompt = f"""
        You are an expert AI Teaching Assistant.

        A multiple-choice question has been generated:

        {response.content}

        Your task is to:
        1. Identify the correct answer (A, B, C, or D).
        2. Explain why that answer is correct.
        3. Optionally, explain why the other options are incorrect.
        4. Return your response in the following format:

        Correct Answer: <A/B/C/D>  
        Explanation: <Your explanation here>
        """.strip()

        # Send this prompt to GPT
        answer_response = model2.invoke(answer_extraction_prompt)
        print("##ANSWER EXTRACTION##", answer_response.content)

        return response.content
    else:
        print("Warning: OpenAI not configured, returning mock question")
        return f"""Question: What is the main concept related to {topic}?
A. Option A
B. Option B  
C. Option C
D. Option D"""
