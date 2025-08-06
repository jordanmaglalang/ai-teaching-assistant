from pinecone import Pinecone, ServerlessSpec
from extract_content import get_text_from_ppt, get_text_from_pdf, pptx_path
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()
api_key = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=api_key) if api_key else None
index_name = "developer-quickstart-py"
query = " What is EAX What is the difference between the following x86 registers: AX, EAX, RAX? (select the best answer) A) Their bit length B) Whether they are byte addressable C) They are different registers"


def initialize_vector_db(index_name):
    # Delete existing index if it exists
    # Create a dense index with integrated embedding
    if not pc:
        print("Warning: Pinecone client not initialized (missing API key)")
        return False

    if not pc.has_index(index_name):
        pc.create_index_for_model(
            name=index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model":"llama-text-embed-v2",
                "field_map":{"text": "chunk_text"}
            }
        )
    return True
  
def prepare_vector_index(file, tutor_id):
    if file.filename.endswith(".pdf"):
        doc_text = get_text_from_pdf(file)
    elif file.filename.endswith(".pptx"):
        doc_text = get_text_from_ppt(file)
    else:
        raise ValueError("Unsupported file type")

    chunks = split_into_chunks(doc_text)
    print(f"Split text into {len(chunks)} chunks.")
    records = []
    for i, chunk in enumerate(chunks):
        records.append({
            "_id": f"{tutor_id}-chunk-{i}",
            "chunk_text": chunk,
            "metadata":  str(tutor_id)
        })

    initialize_vector_db(index_name)
    index = pc.Index(index_name)

    # ✅ Use tutor_id as namespace
    #namespace = str(tutor_id)
    namespace = "6882f38474f97b6061ec2b9e"  # Example namespace, replace with actual tutor_id if needed

    print(f"Upserting {len(records)} chunks to namespace {namespace}")
    index.upsert_records(namespace, records)
    print("Upsert complete")


def prepare_topic_vector_index(file, content, topic, material_id):
    """
    Prepare vector index for teacher materials with topic-based namespacing
    """
    try:
        if not pc:
            print("Warning: Pinecone not configured, skipping vector indexing")
            return
            
        chunks = split_into_chunks(content)
        print(f"Split text into {len(chunks)} chunks for topic: {topic}")
        
        records = []
        for i, chunk in enumerate(chunks):
            records.append({
                "_id": f"{material_id}-chunk-{i}",
                "chunk_text": chunk,
                "metadata": {
                    "material_id": material_id,
                    "topic": topic,
                    "chunk_index": i
                }
            })

        if not initialize_vector_db(index_name):
            print("Failed to initialize vector database")
            return
            
        index = pc.Index(index_name)

        # Use topic as namespace (sanitize topic name for namespace)
        namespace = sanitize_namespace_name(topic)
        
        print(f"Upserting {len(records)} chunks to namespace '{namespace}' for topic '{topic}'")
        index.upsert_records(namespace, records)
        print("Topic-based upsert complete")
        
    except Exception as e:
        print(f"Error in prepare_topic_vector_index: {str(e)}")
        raise

def semantic_search_by_topic(topic, query, top_k=5):
    """
    Search for content within a specific topic namespace
    """
    try:
        if not pc:
            print("Warning: Pinecone not configured, returning empty results")
            return []
            
        index = pc.Index(index_name)
        namespace = sanitize_namespace_name(topic)
        
        print(f"Searching in topic '{topic}' (namespace: '{namespace}') for query: {query}")
        
        results = index.search(
            namespace=namespace,
            query={
                "top_k": top_k,
                "inputs": {
                    "text": query
                }
            }
        )

        results_list = []
        if not results['result']['hits']:
            print(f"No results found for topic '{topic}'")
        else:
            for hit in results['result']['hits']:
                results_list.append({
                    "text": hit['fields']['chunk_text'],
                    "score": hit['_score'],
                    "material_id": hit['metadata'].get('material_id'),
                    "topic": hit['metadata'].get('topic'),
                    "chunk_index": hit['metadata'].get('chunk_index')
                })
        
        return results_list
        
    except Exception as e:
        print(f"Error in semantic_search_by_topic: {str(e)}")
        return []

def get_available_topics():
    """
    Get list of available topics (namespaces) in the vector database
    """
    try:
        index = pc.Index(index_name)
        # Note: Pinecone doesn't have a direct way to list namespaces
        # This would typically be maintained separately in your application
        # For now, we'll return a placeholder
        return ["Data Structures", "Biology", "Mathematics", "Computer Science", "Physics"]
    except Exception as e:
        print(f"Error getting available topics: {str(e)}")
        return []

def sanitize_namespace_name(topic):
    """
    Sanitize topic name to be valid Pinecone namespace
    Pinecone namespaces must be alphanumeric with hyphens and underscores only
    """
    import re
    # Replace spaces and special characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', topic.lower())
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized or "general"


def split_into_chunks(text, max_words=100, overlap=30):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words - overlap):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks
   

def semantic_search(query):
    context_list =[]
    results_list = []
    index = pc.Index(index_name)
    print("Query is, ", query)
    results = index.search(
        namespace="6882f38474f97b6061ec2b9e",
        query={
            "top_k": 3,
            "inputs": {
                "text": query
            }
        }
    )

    if not results['result']['hits']:
        print("no results")
    else:
        for hit in results['result']['hits']:
            
            #print(f"Chunk {hit['_id'][-1]} (score: {hit['_score']}):  Content of chunk {hit['_id'][-1]} : {hit['fields']['chunk_text']}")
            context_list.append(f"Chunk {hit['_id'][-1]} (score: {hit['_score']}):  Content of chunk {hit['_id'][-1]} : {hit['fields']['chunk_text']}")
            results_list.append({
                "text": hit['fields']['chunk_text'],
                "score": hit['_score']
            })
    #result = '\n\n'.join(context_list)

    
    #print(result)
    return results_list
"""
def main():
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
    semantic_search(query)

"""
