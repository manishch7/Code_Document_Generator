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
        process_code_snippet(user_code)

def process_code_snippet(user_code):
    """Process and store the pasted code snippet."""
    if not user_code.strip():
        return
        
    # Create a unique name for the snippet
    snippet_count = len(st.session_state.get("snippet_chunks", []))
    snippet_name = f"snippet_{snippet_count + 1}"
    
    # Let the enhanced generate.py handle code type inference
    metadata = {'file': snippet_name, 'name': 'code_snippet', 'type': 'Code'}
    
    with st.status("Generating professional documentation..."):
        docs = generate_documentation(user_code, metadata)
        
        # Create a chunk for this snippet to be available in chat
        snippet_chunk = {
            'id': snippet_name,
            'code': user_code,
            'metadata': metadata
        }
        
        # Initialize snippet_chunks if it doesn't exist
        if "snippet_chunks" not in st.session_state:
            st.session_state.snippet_chunks = []
            
        # Store the snippet in session state
        st.session_state.snippet_chunks.append(snippet_chunk)
        
        # Initialize snippet_files if it doesn't exist
        if "snippet_files" not in st.session_state:
            st.session_state.snippet_files = []
            
        # Add the snippet file to available files
        if snippet_name not in st.session_state.snippet_files:
            st.session_state.snippet_files.append(snippet_name)
            
        # Initialize selected_snippet_files if it doesn't exist
        if "selected_snippet_files" not in st.session_state:
            st.session_state.selected_snippet_files = []
            
        # Add the snippet to selected files for chat
        if snippet_name not in st.session_state.selected_snippet_files:
            st.session_state.selected_snippet_files.append(snippet_name)
        
        # Display documentation with download option
        st.markdown(docs)
        
        # Use a professional filename
        st.download_button(
            label="Download Documentation",
            data=docs,
            file_name=f"{snippet_name}_documentation.md",
            mime="text/markdown",
            key=f"download_{snippet_name}"
        )
