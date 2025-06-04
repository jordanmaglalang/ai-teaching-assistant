from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="PINECONE_API_KEY")
index_name = "developer-quickstart-py"
query = "Famous historical structures and monuments"
def initialize_vector_db(index_name):
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
def semantic_search(query):
    

    results = index.search(
        namespace="ns1",
        query={
            "top_k": 5,
            "inputs": {
                'text': query
            }
        }
    )

    print(results)

initialize_vector_db(index_name)