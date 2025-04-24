import openai
import os
from typing import Dict, List, Any
from config import OPENAI_API_KEY
from .prompts import STANDARDIZED_DOC_PROMPT, PROJECT_DOCUMENTATION_PROMPT
from .context_retriever import get_context_for_code
from .code_analyzer import infer_code_type
from src.processing.project_analyzer import generate_project_summary

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
LLM_MODEL = "gpt-4o-mini-2024-07-18"

def generate_documentation(code: str, metadata: Dict[str, str]) -> str:
    """
    Generate standardized professional documentation for the provided code.
    
    Args:
        code: The Python code to document
        metadata: Dictionary with file, name, and type information
        
    Returns:
        Markdown formatted documentation
    """
    # If code type is generic, try to infer it
    if metadata['type'] in ['Code', 'code_snippet']:
        code_type, code_name = infer_code_type(code)
        metadata = {
            'file': metadata['file'],
            'name': code_name,
            'type': code_type
        }
    
    # For files, use the filename as name if not provided
    if metadata['type'] in ['File', 'Module'] and metadata['name'] == 'code_snippet':
        metadata['name'] = os.path.basename(metadata['file']) if metadata['file'] != 'user_input' else 'Module'
    
    # Retrieve relevant context
    context = get_context_for_code(metadata)

    # Use standardized prompt for all code types
    prompt = STANDARDIZED_DOC_PROMPT.format(
        code=code,
        metadata=metadata,
        context=context
    )

    # Call LLM
    resp = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional technical writer specializing in creating clear, accurate, and comprehensive software documentation."},
            {"role": "user", "content": prompt}
        ]
    )
    return resp.choices[0].message.content

def generate_project_documentation(project_info: Dict[str, Any], chunks: List[Dict[str, Any]]) -> str:
    """
    Generate comprehensive documentation for an entire project.
    
    Args:
        project_info: Dictionary with project structure information
        chunks: List of code chunks from the project
        
    Returns:
        Markdown formatted project documentation
    """
    # Create context from all chunks for project overview
    context = "Project Structure:\n" + generate_project_summary(project_info)
    
    # Group chunks by module/directory for better organization
    modules = {}
    for chunk in chunks:
        file_path = chunk['metadata']['file']
        directory = os.path.dirname(file_path)
        
        if directory not in modules:
            modules[directory] = []
        
        modules[directory].append(chunk)
    
    # Create a high-level summary of each module
    module_summaries = {}
    for module_path, module_chunks in modules.items():
        # Combine all code from this module
        module_name = module_path if module_path else "root"
        combined_code = f"# Module: {module_name}\n\n"
        
        for chunk in module_chunks:
            combined_code += f"## {chunk['metadata']['type']}: {chunk['metadata']['name']}\n"
            combined_code += chunk['code'] + "\n\n"
        
        # Generate documentation for this module
        module_metadata = {
            'file': module_path,
            'name': module_name,
            'type': 'Module'
        }
        
        module_docs = generate_documentation(combined_code, module_metadata)
        module_summaries[module_name] = module_docs
    
    # Create project-level documentation
    project_name = project_info['root_dir']
    project_prompt = PROJECT_DOCUMENTATION_PROMPT.format(
        project_name=project_name,
        project_structure=generate_project_summary(project_info),
        key_modules=', '.join(modules.keys())
    )
    
    # Call LLM for project-level docs
    project_docs_response = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional technical writer specializing in creating clear, accurate, and comprehensive software documentation."},
            {"role": "user", "content": project_prompt}
        ]
    )
    
    project_docs = project_docs_response.choices[0].message.content
    
    # Combine all documentation
    full_docs = f"# {project_name} - Project Documentation\n\n"
    full_docs += project_docs + "\n\n"
    full_docs += "# Module Documentation\n\n"
    
    for module_name, module_docs in module_summaries.items():
        full_docs += f"## Module: {module_name}\n\n"
        full_docs += module_docs + "\n\n"
        full_docs += "---\n\n"
    
    return full_docs

def generate_file_documentation(file_name: str, file_chunks: List[Dict[str, Any]]) -> str:
    """
    Generate documentation for a specific file by combining its chunks.
    
    Args:
        file_name: Name of the file to document
        file_chunks: List of code chunks from the file
        
    Returns:
        Markdown formatted file documentation
    """
    # Combine all chunks from the file into a single context
    combined_code = ""
    for chunk in file_chunks:
        combined_code += f"\n# {chunk['metadata']['type']}: {chunk['metadata']['name']}\n"
        combined_code += chunk['code'] + "\n\n"
    
    # Create metadata for the whole file
    file_metadata = {
        'file': file_name,
        'name': os.path.basename(file_name),
        'type': 'File'
    }
    
    # Generate documentation for the combined code
    docs = generate_documentation(combined_code, file_metadata)
    
    return docs