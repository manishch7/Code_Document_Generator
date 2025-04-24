import openai
from pinecone import Pinecone
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX

# Re-init clients
openai.api_key = OPENAI_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

EMBED_MODEL = "text-embedding-3-small"  # Updated from "text-embedding-ada-002"

def semantic_search(query: str, top_k: int = 5) -> list:
    """Return top_k code chunks semantically similar to query."""
    q_emb = openai.Embedding.create(model=EMBED_MODEL, input=query)['data'][0]['embedding']
    
    # Updated query format for new Pinecone API
    res = index.query(
        vector=q_emb,
        top_k=top_k,
        include_metadata=True
    )
    
    # Format results according to expected structure
    return [
        {'id': m.id, 'metadata': m.metadata, 'code': m.metadata.get('code', '')}
        for m in res.matches
    ]