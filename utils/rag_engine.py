import chromadb # type: ignore
import google.generativeai as genai # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    # We tell the editor to ignore the 'configure' error
    genai.configure(api_key=api_key) # type: ignore

# Setup ChromaDB
try:
    chroma_client = chromadb.PersistentClient(path="./chroma_db") # type: ignore
    collection = chroma_client.get_or_create_collection(name="fitness_knowledge")
except Exception as e:
    print(f"ChromaDB Error: {e}")
    collection = None

def add_document_to_knowledge(text_chunk):
    if not text_chunk or not text_chunk.strip():
        return False
    
    if not collection:
        return False
        
    try:
        # Force editor to ignore embed_content error
        result = genai.embed_content( # type: ignore
            model="models/text-embedding-004",
            content=text_chunk,
            task_type="retrieval_document"
        )
        
        collection.add(
            documents=[text_chunk],
            embeddings=[result['embedding']],
            ids=[str(abs(hash(text_chunk)))]
        )
        return True
    except Exception as e:
        print(f"RAG Add Error: {e}")
        return False

def search_knowledge(query):
    if not collection:
        return []

    try:
        # Force editor to ignore embed_content error
        result = genai.embed_content( # type: ignore
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        
        results = collection.query(
            query_embeddings=[result['embedding']],
            n_results=3
        )
        
        if results and 'documents' in results and results['documents']:
             if len(results['documents']) > 0:
                return results['documents'][0]
        return []
    except Exception as e:
        print(f"RAG Search Error: {e}")
        return []