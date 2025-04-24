from typing import Dict, List, Any
from src.core.retriever import semantic_search

def get_context_for_code(metadata: Dict[str, str]) -> str:
    """
    Retrieve relevant chunks from the vector store based on code metadata.
    
    Args:
        metadata: Dictionary with information about the code (type, name, file)
        
    Returns:
        String of context from similar code chunks
    """
    query = f"Document {metadata['type']} {metadata['name']}"
    context_chunks = semantic_search(query)
    return "\n---\n".join(c['code'] for c in context_chunks) or "No additional context."

def get_context_for_project(project_name: str, key_modules: List[str]) -> str:
    """
    Retrieve relevant chunks for project-level documentation.
    
    Args:
        project_name: Name of the project
        key_modules: List of key module names in the project
        
    Returns:
        String of context from relevant code chunks
    """
    # Build a query that captures the project structure
    query = f"Document project {project_name} with modules {', '.join(key_modules)}"
    context_chunks = semantic_search(query)
    
    # Format the context for use in documentation
    formatted_context = ""
    for chunk in context_chunks:
        formatted_context += f"FILE: {chunk['metadata']['file']}\n"
        formatted_context += f"{chunk['code']}\n\n"
    
    return formatted_context or "No additional context available."