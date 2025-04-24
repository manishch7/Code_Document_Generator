# Standard documentation prompt template
STANDARDIZED_DOC_PROMPT = """
Write professional documentation for the following Python code:

CODE:
```python
{code}
```

METADATA:
- File: {metadata[file]}
- Type: {metadata[type]}
- Name: {metadata[name]}

ADDITIONAL CONTEXT FROM CODEBASE:
{context}

Your documentation should include:
1. A clear overview of what this code does
2. Function/class/module level documentation with parameters, return values, and usage
3. Clear examples of how to use this code (if applicable)
4. Explanations of any complex algorithms or logic
5. Notes about edge cases or potential issues

The documentation should be professional, clear, and follow Python documentation best practices.
Use markdown formatting with appropriate headings, code blocks, and bullet points.
"""

PROJECT_DOCUMENTATION_PROMPT = """
You are documenting an entire Python project. Generate comprehensive project-level documentation.

PROJECT NAME: {project_name}

PROJECT STRUCTURE:
{project_structure}

KEY MODULES:
{key_modules}

Based on this information, create professional project-level documentation that explains:

1. The overall architecture of the project
2. How the different modules interact with each other
3. Key design patterns and principles used
4. System dependencies and requirements
5. How to use and extend the project

Your documentation should follow a professional structure with clear headings and proper technical terminology.
"""