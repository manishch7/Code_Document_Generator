import streamlit as st
import tempfile
import os
import shutil
from src.core.chunker import extract_chunks
from src.core.embeddings import upsert_chunks
from src.core.documentation import generate_file_documentation

def render_file_tab():
    """Render the File Documentation tab UI and functionality."""
    st.header("File Documentation")
    
    # Main area: Upload files (moved from sidebar)
    st.subheader("Upload Python Files")
    uploaded_files = st.file_uploader("Upload Python files", accept_multiple_files=True, type=["py"])
    
    # Process files
    if uploaded_files and st.button("Process Files"):
        process_uploaded_files(uploaded_files)
    
    # Generate docs for each file
    if st.session_state.processed_chunks:
        st.header("Generate Documentation")
        
        if st.button("Generate Documentation for All Files"):
            generate_all_file_documentation()
        
        # Add option to view previously generated documentation
        if st.session_state.file_documentation:
            display_file_documentation()
    else:
        # No files processed yet
        st.info("Upload Python files and click 'Process Files' to get started, or use the Project Documentation tab to process an entire project ZIP.")

def process_uploaded_files(uploaded_files):
    """Process uploaded Python files and extract code chunks."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded files to temp directory
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # Extract and index chunks
        with st.status("Processing files..."):
            chunks = extract_chunks(temp_dir)
            
            if chunks:
                # Store chunks in session state
                st.session_state.processed_chunks = chunks
                
                # Track available files
                st.session_state.available_files = list(set(chunk['metadata']['file'] for chunk in chunks))
                
                # Upsert chunks to vector database
                upsert_chunks(chunks)
                st.success(f"Processed {len(chunks)} code chunks from {len(uploaded_files)} files.")
            else:
                st.error("No valid code chunks found in the uploaded files.")

def generate_all_file_documentation():
    """Generate documentation for all processed files."""
    with st.status("Generating professional documentation..."):
        # Group chunks by file for better organization
        files = {}
        for chunk in st.session_state.processed_chunks:
            file_name = chunk['metadata']['file']
            if file_name not in files:
                files[file_name] = []
            files[file_name].append(chunk)
        
        # Generate documentation for each file
        for file_name, file_chunks in files.items():
            st.subheader(f"File: {file_name}")
            
            # Generate documentation for this file
            docs = generate_file_documentation(file_name, file_chunks)
            
            # Store documentation in session state
            st.session_state.file_documentation[file_name] = {
                'docs': docs
            }
            
            # Display documentation with download button
            st.markdown(docs)
            st.download_button(
                label="Download Documentation",
                data=docs,
                file_name=f"{os.path.basename(file_name)}_documentation.md",
                mime="text/markdown",
                key=f"download_{file_name}"
            )
            
            st.divider()

def display_file_documentation():
    """Display previously generated file documentation."""
    st.header("Access Generated Documentation")
    
    # Create selectbox for choosing documentation
    file_options = list(st.session_state.file_documentation.keys())
    
    selected_file = st.selectbox("Select file to view documentation", file_options)
    
    if selected_file:
        result = st.session_state.file_documentation[selected_file]
        
        # Show documentation in expandable section
        with st.expander("Documentation", expanded=True):
            st.markdown(result['docs'])
            st.download_button(
                label="Download Documentation",
                data=result['docs'],
                file_name=f"{os.path.basename(selected_file)}_documentation.md",
                mime="text/markdown",
                key=f"download_viewer_{selected_file}"
            )