import streamlit as st
import tempfile
import os
import shutil
import openai
from config import OPENAI_API_KEY

# Import processing modules
from src.processing.zip_handler import process_zip_file, list_all_files_in_directory
from src.processing.project_analyzer import analyze_project_structure, generate_project_summary
from src.core.chunker import extract_chunks
from src.core.embeddings import upsert_chunks
from src.core.documentation import generate_project_documentation

def render_project_tab():
    """Render the Project Documentation tab UI and functionality."""
    st.header("Generate Documentation for Complete Project")
    st.info("Upload a ZIP file containing your entire project to generate comprehensive documentation. "
            "Only Python (.py) files will be processed, other files (images, videos, etc.) will be ignored.")
    
    # Upload ZIP file
    uploaded_zip = st.file_uploader("Upload Project ZIP File", type=["zip"])
    
    # Debug mode toggle
    debug_mode = st.checkbox("Enable Debug Mode", 
                           help="Show detailed information about the ZIP processing")
    
    if uploaded_zip:
        # Show project processing button
        if st.button("Process Project and Generate Documentation"):
            process_uploaded_project(uploaded_zip, debug_mode)
    
    # Display project documentation if available
    if st.session_state.project_documentation:
        display_project_documentation()

def process_uploaded_project(uploaded_zip, debug_mode):
    """Process the uploaded ZIP file and generate documentation."""
    with st.status("Processing project...") as status:
        # Save uploaded zip to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
            tmp_zip.write(uploaded_zip.getvalue())
            zip_path = tmp_zip.name
        
        status.update(label="Extracting ZIP file (Python files only)...")
        # Extract the zip file with extended debug info
        extract_dir, file_stats = process_zip_file(zip_path)
        
        # Debug info display
        display_debug_info(debug_mode, extract_dir, file_stats)
        
        # Check if any Python files were found in the ZIP
        if not handle_python_files_check(status, debug_mode, extract_dir, file_stats):
            return
            
        # Analyze project structure
        status.update(label="Analyzing project structure...")
        project_info = analyze_project_structure(extract_dir)
        
        if debug_mode:
            st.subheader("Project Structure Analysis")
            st.json(project_info)
        
        # Generate project summary
        status.update(label="Generating project summary...")
        project_summary = generate_project_summary(project_info)
        st.session_state.project_summary = project_summary
        
        # Check again if Python files are found after directory analysis
        if project_info['py_file_count'] == 0:
            status.update(label="No Python files found in the extracted directory!", state="error")
            st.error("Although the ZIP contains Python files, they couldn't be properly extracted or processed. "
                    "Please check your ZIP file structure.")
            
            if debug_mode:
                st.write("All files found in the extracted directory:")
                st.write(project_info['all_files'])
            return
        
        # Extract code chunks
        status.update(label=f"Extracting code chunks from {project_info['py_file_count']} Python files...")
        chunks = extract_chunks(extract_dir)
        
        if not chunks:
            status.update(label="No valid code chunks found in Python files!", state="error")
            st.error("The Python files in the ZIP could not be parsed into valid code chunks.")
            
            if debug_mode:
                st.write("Python files found but couldn't be parsed:")
                st.write(project_info['python_files'])
            return
            
        # Store chunks in session state - both in the general variable and project-specific
        st.session_state.processed_chunks = chunks
        st.session_state.project_chunks = chunks
        
        # Track available files
        st.session_state.available_files = list(set(chunk['metadata']['file'] for chunk in chunks))
        st.session_state.project_files = st.session_state.available_files.copy()
        
        # Also update selected files for chat to include newly processed files
        if not st.session_state.selected_project_files:
            st.session_state.selected_project_files = st.session_state.project_files.copy()
        
        # Upsert chunks to vector database
        status.update(label="Indexing code for search...")
        upsert_chunks(chunks)
        
        # Generate project documentation
        status.update(label="Generating comprehensive project documentation...")
        project_docs = generate_project_documentation(project_info, chunks)
        st.session_state.project_documentation = project_docs
        
        status.update(label=f"Documentation complete! Processed {len(chunks)} code chunks from "
                     f"{project_info['py_file_count']} Python files.", state="complete")
        
        # Clean up temporary files unless in debug mode
        if not debug_mode:
            try:
                os.unlink(zip_path)
                shutil.rmtree(extract_dir)
            except:
                pass

def display_debug_info(debug_mode, extract_dir, file_stats):
    """Display debug information if debug mode is enabled."""
    if debug_mode:
        st.subheader("ZIP File Contents")
        st.json(file_stats)
        
        st.subheader("All Files in ZIP")
        st.write(file_stats['all_files'])
        
        st.subheader("Extracted Files")
        st.write(file_stats['extracted_files'])
        
        st.subheader("Files in Extracted Directory")
        directory_files = list_all_files_in_directory(extract_dir)
        st.write(directory_files)

def handle_python_files_check(status, debug_mode, extract_dir, file_stats):
    """Check if Python files were found and handle the error case."""
    if file_stats['python_files'] == 0:
        if debug_mode:
            # In debug mode, try to analyze the directory anyway
            st.warning("No Python files detected in ZIP metadata, but checking extracted directory...")
            
            # List all files in the extracted directory
            all_extracted = list_all_files_in_directory(extract_dir)
            python_files = [f for f in all_extracted if f.endswith('.py')]
            
            if python_files:
                st.success(f"Found {len(python_files)} Python files in the extracted directory!")
                st.write(python_files)
                return True
            else:
                status.update(label="No Python files found in ZIP!", state="error")
                st.error("No Python files were found in the uploaded ZIP. "
                         "Please ensure your ZIP file contains Python (.py) files.")
                
                # Display a more detailed error with file types found
                extensions = {}
                for file in file_stats['all_files']:
                    ext = os.path.splitext(file.lower())[1]
                    if ext:
                        extensions[ext] = extensions.get(ext, 0) + 1
                
                st.write("File types found in the ZIP:")
                st.json(extensions)
                return False
        else:
            status.update(label="No Python files found in ZIP!", state="error")
            st.error("No Python files were found in the uploaded ZIP. "
                     "Please ensure your ZIP file contains Python (.py) files.")
            return False
    return True

def display_project_documentation():
    """Display project documentation with download buttons."""
    st.header("Project Documentation")
    
    # Display the documentation with download button
    st.markdown(st.session_state.project_documentation)
    
    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Complete Documentation",
            data=st.session_state.project_documentation,
            file_name="project_documentation.pdf",
            mime="text/markdown",
            key=f"download_project_docs"
        )
    
    with col2:
        if st.session_state.project_summary:
            st.download_button(
                label="Download Project Structure Summary",
                data=st.session_state.project_summary,
                file_name="project_structure.pdf",
                mime="text/markdown",
                key=f"download_project_summary"
            )
