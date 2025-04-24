import openai
from pinecone import Pinecone, ServerlessSpec
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX
from typing import List, Dict, Any

# Initialize clients
openai.api_key = OPENAI_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)

# Embedding model
EMBED_MODEL = "text-embedding-3-small"

def initialize_pinecone_index() -> None:
    """Create Pinecone index if it doesn't exist."""
    index_list = [index.name for index in pc.list_indexes()]
    if PINECONE_INDEX not in index_list:
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-west-2"
            )
        )

def get_pinecone_index():
    """Get the Pinecone index, initializing it if needed."""
    initialize_pinecone_index()
    return pc.Index(PINECONE_INDEX)

def embed_text(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text.
    
    Args:
        text: The text to embed
        
    Returns:
        List of embedding values
    """
    resp = openai.Embedding.create(model=EMBED_MODEL, input=text)
    return resp['data'][0]['embedding']

def upsert_chunks(chunks: List[Dict[str, Any]]):
    """
    Embed code chunks and upsert into Pinecone.
    
    Args:
        chunks: List of chunk dictionaries with 'id', 'code', and 'metadata'
    """
    vectors = []
    for c in chunks:
        vec = embed_text(c['code'])
        # include code in metadata for easy retrieval
        meta = c['metadata'].copy()
        meta['code'] = c['code']
        vectors.append((c['id'], vec, meta))
    
    # Batch upsert to Pinecone
    # Convert to format expected by new Pinecone API
    pinecone_vectors = [
        {"id": id, "values": vec, "metadata": meta}
        for id, vec, meta in vectors
    ]
    
    index = get_pinecone_index()
    
    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(pinecone_vectors), batch_size):
        batch = pinecone_vectors[i:i+batch_size]
        index.upsert(vectors=batch)
    
    print(f"Upserted {len(vectors)} chunks to Pinecone.")