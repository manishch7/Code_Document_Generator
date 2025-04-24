from langchain_core.prompts import PromptTemplate

FUNCTION_DOC_PROMPT = PromptTemplate(
    input_variables=["code", "metadata", "context"],
    template="""
You are an expert Python developer and technical writer who specializes in creating professional documentation.

Context from related code in the project:
{context}

I'll provide you with Python code to document. The code is of type {metadata[type]} and is named `{metadata[name]}` from file {metadata[file]}.

```python
{code}
```

Generate clear, professional documentation that explains both WHAT the code does and WHY it does it. Include:

### FOR ALL CODE TYPES:
1. **Summary**: Clear explanation of what this code does in straightforward terms
2. **Workflow**: Step-by-step breakdown of how the code works
3. **Key Concepts**: Explanation of important programming concepts or patterns used
4. **Dependencies**: What external libraries, functions, or data this code relies on
5. **Purpose**: The business or technical problem this code solves

### ADDITIONAL SECTIONS BASED ON CODE TYPE:

**If Module (entire file):**
6. **Functions/Classes Overview**: List each function/class with a brief description
7. **Data Flow**: How information moves through this module
8. **Execution Flow**: The sequence of operations when the module runs

**If Function/AsyncFunction:**
6. **Parameters**: For each parameter:
   - Type
   - Purpose
   - Default value (if any)
   - Required or optional status
7. **Return Value**: What it returns and how to use it
8. **Errors/Exceptions**: What could go wrong and how it's handled

**If Class:**
6. **Class Structure**: How the class is organized
7. **Attributes**: All important properties with types and purposes
8. **Methods**: Key methods with brief descriptions
9. **Lifecycle**: How instances are created, used, and destroyed

### FOR ALL CODE TYPES:
9. **Example**: A clear, annotated example showing how to use this code
10. **Customization Options**: How to adapt this code for different needs
11. **Limitations and Edge Cases**: Important constraints or special cases to be aware of

Structure your documentation with clear, professional section headers. Use concrete examples rather than abstract descriptions where possible.
"""
)