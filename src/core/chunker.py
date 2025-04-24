import ast
import os
import traceback
from asttokens import ASTTokens
from typing import List, Dict, Any

def extract_chunks(source_dir: str) -> List[Dict[str, Any]]:
    """
    Walk through .py files under source_dir and extract each
    class/function as a code chunk with metadata.
    
    Args:
        source_dir: Directory containing Python files
        
    Returns:
        List of dictionaries with 'id', 'code', and 'metadata' keys
    """
    chunks = []
    print(f"Searching for Python files in: {source_dir}")
    
    for root, _, files in os.walk(source_dir):
        print(f"Checking directory: {root}")
        print(f"Files found: {files}")
        
        for fname in files:
            if not fname.endswith('.py'):
                continue
                
            print(f"Processing Python file: {fname}")
            path = os.path.join(root, fname)
            
            try:
                with open(path, encoding='utf-8') as f:
                    src = f.read()
                
                print(f"File content length: {len(src)} chars")
                print(f"First 100 chars of file: {src[:100].replace(chr(10), ' ')}")
                
                # If file doesn't contain any functions or classes, create a chunk for the entire file
                has_functions_or_classes = False
                
                try:
                    # Parse the AST
                    atok = ASTTokens(src, parse=True)
                    
                    # Count nodes for debugging
                    function_count = 0
                    class_count = 0
                    
                    for node in ast.walk(atok.tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            has_functions_or_classes = True
                            function_count += 1
                            code = atok.get_text(node)
                            obj_id = f"{os.path.relpath(path, source_dir)}::{node.name}"
                            metadata = {
                                'file': os.path.relpath(path, source_dir),
                                'name': node.name,
                                'type': type(node).__name__
                            }
                            chunks.append({'id': obj_id, 'code': code, 'metadata': metadata})
                            print(f"Added function: {node.name}")
                            
                        elif isinstance(node, ast.ClassDef):
                            has_functions_or_classes = True
                            class_count += 1
                            code = atok.get_text(node)
                            obj_id = f"{os.path.relpath(path, source_dir)}::{node.name}"
                            metadata = {
                                'file': os.path.relpath(path, source_dir),
                                'name': node.name,
                                'type': type(node).__name__
                            }
                            chunks.append({'id': obj_id, 'code': code, 'metadata': metadata})
                            print(f"Added class: {node.name}")
                    
                    print(f"Found {function_count} functions and {class_count} classes in {fname}")
                    
                    # If no functions or classes were found, add the whole file as a chunk
                    if not has_functions_or_classes:
                        print(f"No functions or classes found in {fname}, adding entire file as a chunk")
                        obj_id = f"{os.path.relpath(path, source_dir)}::whole_file"
                        metadata = {
                            'file': os.path.relpath(path, source_dir),
                            'name': os.path.basename(path),
                            'type': 'Module'
                        }
                        chunks.append({'id': obj_id, 'code': src, 'metadata': metadata})
                    
                except SyntaxError as e:
                    print(f"Syntax error in {path}: {e}")
                    print(f"Line {e.lineno}, column {e.offset}: {e.text}")
                    
                    # Even if there's a syntax error, try to add the file as a chunk
                    print(f"Adding file with syntax error as a chunk")
                    obj_id = f"{os.path.relpath(path, source_dir)}::whole_file"
                    metadata = {
                        'file': os.path.relpath(path, source_dir),
                        'name': os.path.basename(path),
                        'type': 'Module'
                    }
                    chunks.append({'id': obj_id, 'code': src, 'metadata': metadata})
                    
            except Exception as e:
                print(f"Error processing {path}: {e}")
                print(traceback.format_exc())
    
    print(f"Total chunks extracted: {len(chunks)}")
    return chunks