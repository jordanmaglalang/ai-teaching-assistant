from langchain_community.tools import tool
from vector_db import semantic_search

@tool
def retrieve_relevant_chunks(query:str)->str:
    """
    Retrieve the top 3 relevant chunks from Pinecone given a semantic query.
    """
    print("##RUN TOOL 1##")
    return semantic_search(query)