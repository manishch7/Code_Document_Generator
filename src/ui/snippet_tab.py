import streamlit as st
from src.core.documentation import generate_documentation

def render_snippet_tab():
    """Render the Code Snippet Documentation tab UI and functionality."""
    st.header("Generate Documentation for Code Snippet")
    user_code = st.text_area(
        "Paste your code here:", 
        height=300, 
        placeholder="Paste your Python code here (function, class, or complete module)..."
    )
    
    if st.button("Generate Professional Documentation") and user_code.strip():
        # Let the enhanced generate.py handle code type inference
        metadata = {'file': 'user_input', 'name': 'code_snippet', 'type': 'Code'}
        
        with st.status("Generating professional documentation..."):
            docs = generate_documentation(user_code, metadata)
            
            # Display documentation with download option
            st.markdown(docs)
            
            # Use a professional filename
            st.download_button(
                label="Download Documentation",
                data=docs,
                file_name="code_documentation.md",
                mime="text/markdown",
                key="download_pasted_code"
            )
