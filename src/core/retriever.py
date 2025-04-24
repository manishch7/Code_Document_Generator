import openai
from typing import List, Dict, Any
from pinecone import Pinecone
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX
from src.core.embeddings import embed_text

# Initialize clients
openai.api_key = OPENAI_API_KEY
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

def semantic_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Return top_k code chunks semantically similar to query.
    
    Args:
        query: The search query
        top_k: Number of results to return
        
    Returns:
        List of matching code chunks with their metadata
    """
    # Generate embedding for the query
    q_emb = embed_text(query)
    
    # Query Pinecone
    res = index.query(
        vector=q_emb,
        top_k=top_k,
        include_metadata=True
    )
    
    # Format results
    return [
        {'id': m.id, 'metadata': m.metadata, 'code': m.metadata.get('code', '')}
        for m in res.matches
    ]