import os
from typing import Dict, List

def analyze_project_structure(project_dir: str) -> Dict:
    """
    Analyze the directory structure of a project.
    Only considers Python files and ignores media/binary files.
    
    Args:
        project_dir: Path to the project directory
        
    Returns:
        Dictionary with project structure information
    """
    project_info = {
        'root_dir': os.path.basename(project_dir),
        'python_files': [],
        'directories': [],
        'file_count': 0,
        'py_file_count': 0,
        'directory_count': 0,
        'modules': {},
        'top_level_modules': [],
        'all_files': []  # Track all files for debugging
    }
    
    # Walk through the directory
    for root, dirs, files in os.walk(project_dir):
        # For debugging, track all files
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, project_dir)
            project_info['all_files'].append(rel_path)
        
        # Skip hidden directories (like .git, __pycache__)
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        # Add directories
        rel_path = os.path.relpath(root, project_dir)
        if rel_path != '.':
            project_info['directories'].append(rel_path)
            project_info['directory_count'] += 1
        
        # Create module info
        module_name = rel_path.replace(os.path.sep, '.')
        if module_name == '.':
            module_name = 'root'
        
        # Filter for Python files
        python_files = [f for f in files if f.endswith('.py')]
        
        # Only create module entry if there are Python files
        if python_files:
            if module_name == 'root':
                project_info['top_level_modules'] = [
                    f[:-3] for f in python_files if f != '__init__.py'
                ]
            
            project_info['modules'][module_name] = {
                'files': python_files,
                'path': rel_path
            }
        
        # Process files (only count Python files)
        for file in files:
            if file.endswith('.py'):
                project_info['file_count'] += 1
                file_path = os.path.join(rel_path, file)
                project_info['python_files'].append(file_path)
                project_info['py_file_count'] += 1
    
    return project_info

def generate_project_summary(project_info: Dict) -> str:
    """
    Generate a summary of the project structure.
    
    Args:
        project_info: Dictionary with project structure information
        
    Returns:
        Markdown string with project summary
    """
    summary = f"# Project Structure: {project_info['root_dir']}\n\n"
    
    # Basic statistics
    summary += "## Project Statistics\n"
    summary += f"- Python files: {project_info['py_file_count']}\n"
    summary += f"- Directories: {project_info['directory_count']}\n\n"
    
    # Top-level modules
    if project_info['top_level_modules']:
        summary += "## Top-level Modules\n"
        for module in project_info['top_level_modules']:
            summary += f"- `{module}`\n"
        summary += "\n"
    
    # Module structure
    summary += "## Module Structure\n"
    for module_name, module_info in project_info['modules'].items():
        if module_name == 'root':
            continue
        
        summary += f"### {module_name}\n"
        summary += f"- Path: `{module_info['path']}`\n"
        summary += "- Files:\n"
        for file in module_info['files']:
            summary += f"  - `{file}`\n"
        summary += "\n"
    
    return summary