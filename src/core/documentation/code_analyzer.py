import ast
import re
from typing import Tuple, Dict, Any, List

def infer_code_type(code: str) -> Tuple[str, str]:
    """
    Infer the type and name of the provided code snippet.
    
    Args:
        code: The Python code to analyze
        
    Returns:
        A tuple of (type, name)
    """
    # First try parsing with AST
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                return ("ClassDef", node.name)
            elif isinstance(node, ast.FunctionDef):
                return ("FunctionDef", node.name)
        
        # If we get here, it's likely a module or snippet without class/function
        return ("Module", "Module")
    except SyntaxError:
        # If parsing fails, use regex to try to infer the type
        class_match = re.search(r'class\s+([a-zA-Z0-9_]+)', code)
        if class_match:
            return ("ClassDef", class_match.group(1))
        
        func_match = re.search(r'def\s+([a-zA-Z0-9_]+)', code)
        if func_match:
            return ("FunctionDef", func_match.group(1))
        
        # Default fallback
        return ("Code", "CodeSnippet")

def analyze_imports(code: str) -> List[str]:
    """
    Analyze the import statements in the code to determine dependencies.
    
    Args:
        code: The Python code to analyze
        
    Returns:
        List of imported modules/packages
    """
    imports = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except SyntaxError:
        # If parsing fails, use regex as fallback
        import_regex = r'import\s+([a-zA-Z0-9_.]+)|from\s+([a-zA-Z0-9_.]+)\s+import'
        for match in re.finditer(import_regex, code):
            module = match.group(1) or match.group(2)
            if module:
                imports.append(module)
    
    return imports

def extract_docstring(code: str) -> str:
    """
    Extract the docstring from the provided code if one exists.
    
    Args:
        code: The Python code to analyze
        
    Returns:
        The docstring if found, otherwise an empty string
    """
    try:
        tree = ast.parse(code)
        
        # Check for module docstring
        if (len(tree.body) > 0 and 
            isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Str)):
            return tree.body[0].value.s
        
        # Check for class/function docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                # Check if the first element in the body is a docstring
                if (len(node.body) > 0 and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Str)):
                    return node.body[0].value.s
    except SyntaxError:
        # If parsing fails, return empty string
        pass
    
    return ""

def extract_function_info(code: str) -> List[Dict[str, Any]]:
    """
    Extract information about functions in the code.
    
    Args:
        code: The Python code to analyze
        
    Returns:
        List of dictionaries with function information
    """
    functions = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Extract parameters
                params = []
                for arg in node.args.args:
                    params.append(arg.arg)
                
                # Extract docstring if available
                docstring = ""
                if (len(node.body) > 0 and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Str)):
                    docstring = node.body[0].value.s
                
                functions.append({
                    'name': node.name,
                    'async': isinstance(node, ast.AsyncFunctionDef),
                    'params': params,
                    'docstring': docstring
                })
    except SyntaxError:
        pass
    
    return functions