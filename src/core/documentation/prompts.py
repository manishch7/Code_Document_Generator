# Component documentation prompt
STANDARDIZED_DOC_PROMPT = """
Document this Python code:

```python
{code}
```

METADATA: File: {metadata[file]} | Type: {metadata[type]} | Name: {metadata[name]}
CONTEXT: {context}

Include:
1. Brief overview
2. Parameters, return values, usage
3. Example (if applicable)
4. Key algorithms/logic
5. Edge cases

Use markdown with proper headings and code blocks.
"""

# Project documentation prompt
PROJECT_DOCUMENTATION_PROMPT = """
Create concise documentation for this Python project.

PROJECT STRUCTURE: {project_structure}

First, carefully analyze the codebase to determine a meaningful project name based on:
- Main functionality and purpose
- Key features observed in the code
- Main modules and their relationships
- Import statements and dependencies

DO NOT use random characters or generic names. Create a descriptive name that reflects what the project actually does.

Then create documentation with these sections:

1. **Overview:** Purpose, features, problem solved

2. **Requirements:** Python version, dependencies (from requirements.txt)

3. **Setup:** Installation, configuration, first run

4. **Architecture:** 
   - Component interactions
   - Data flow
   - File structure with brief descriptions

5. **Key Components:** Main modules with examples

6. **Usage Examples:** Basic and advanced scenarios

7. **Extension Points:** How to add features

8. **Troubleshooting:** Common issues and solutions

9. **Quick Links:**
   - Create a table of links to important files/components
   - Each link should point to the corresponding file in the project
   - Use markdown link format: [Component Name](relative_path_to_file)
   - Include brief description of what each link provides

Be professional and include proper file structure with descriptions.
"""