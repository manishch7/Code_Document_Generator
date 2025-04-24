import openai
import sys
import os

# Add the project root directory to Python's module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.rag.prompts import FUNCTION_DOC_PROMPT
from src.rag.retriever import semantic_search
from config import OPENAI_API_KEY

# Init OpenAI
openai.api_key = OPENAI_API_KEY
LLM_MODEL = "gpt-4o-mini-2024-07-18"  # You can change this to another available model if needed

def generate_documentation(code: str, metadata: dict) -> str:
    # Retrieve relevant chunks
    query = f"Document {metadata['type']} {metadata['name']}"
    context_chunks = semantic_search(query)
    context = "\n---\n".join(c['code'] for c in context_chunks) or "No additional context."

    # Build prompt
    prompt = FUNCTION_DOC_PROMPT.format(
        code=code,
        metadata=metadata,
        context=context
    )

    # Call LLM
    resp = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return resp.choices[0].message.content