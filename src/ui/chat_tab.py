import streamlit as st
import openai
from config import OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
LLM_MODEL = "gpt-4o-mini-2024-07-18"

def render_chat_tab():
    """Render the Code Chatbot tab UI and functionality."""
    st.header("Code Expert Assistant")
    
    # Check if we have any files processed
    if not st.session_state.get("processed_chunks", []) and not st.session_state.get("project_chunks", []) and not st.session_state.get("file_chunks", []) and not st.session_state.get("snippet_chunks", []):
        st.warning("Please upload and process files in the File Documentation tab, process a project ZIP, or paste code in the Snippet tab first.")
        return
    
    # Initialize specific chunk categories if they don't exist
    if "project_chunks" not in st.session_state:
        st.session_state.project_chunks = []
    
    if "file_chunks" not in st.session_state:
        st.session_state.file_chunks = []
        
    if "snippet_chunks" not in st.session_state:
        st.session_state.snippet_chunks = []
    
    # Track separate file lists for different sources
    if "project_files" not in st.session_state:
        st.session_state.project_files = []
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
        
    if "snippet_files" not in st.session_state:
        st.session_state.snippet_files = []
    
    # Track selected files for each source
    if "selected_project_files" not in st.session_state:
        st.session_state.selected_project_files = []
    
    if "selected_uploaded_files" not in st.session_state:
        st.session_state.selected_uploaded_files = []
        
    if "selected_snippet_files" not in st.session_state:
        st.session_state.selected_snippet_files = []
    
    # Update available files lists from chunks
    available_project_files = list(set(chunk['metadata']['file'] for chunk in st.session_state.project_chunks)) if st.session_state.project_chunks else []
    available_uploaded_files = list(set(chunk['metadata']['file'] for chunk in st.session_state.file_chunks)) if st.session_state.file_chunks else []
    available_snippet_files = list(set(chunk['metadata']['file'] for chunk in st.session_state.snippet_chunks)) if st.session_state.snippet_chunks else []
    
    # Update session state
    st.session_state.project_files = available_project_files
    st.session_state.uploaded_files = available_uploaded_files
    st.session_state.snippet_files = available_snippet_files
    
    # Filter selected files to only include available files (prevent errors)
    st.session_state.selected_project_files = [f for f in st.session_state.selected_project_files if f in available_project_files]
    st.session_state.selected_uploaded_files = [f for f in st.session_state.selected_uploaded_files if f in available_uploaded_files]
    st.session_state.selected_snippet_files = [f for f in st.session_state.selected_snippet_files if f in available_snippet_files]
    
    # File selection UI with tabs for different sources
    st.subheader("Select Files for Context")
    source_tabs = st.tabs(["Project Files", "Uploaded Files", "Code Snippets", "All Files"])
    
    with source_tabs[0]:
        if available_project_files:
            st.multiselect(
                "Select project files:",
                available_project_files,
                default=st.session_state.selected_project_files,
                key="project_files_select"
            )
            # Update selected files when widget value changes
            st.session_state.selected_project_files = st.session_state.project_files_select
        else:
            st.info("No project files available. Please upload a project ZIP in the Project Documentation tab.")
    
    with source_tabs[1]:
        if available_uploaded_files:
            st.multiselect(
                "Select uploaded files:",
                available_uploaded_files,
                default=st.session_state.selected_uploaded_files,
                key="uploaded_files_select"
            )
            # Update selected files when widget value changes
            st.session_state.selected_uploaded_files = st.session_state.uploaded_files_select
        else:
            st.info("No uploaded files available. Please upload individual files in the File Documentation tab.")
    
    with source_tabs[2]:
        if available_snippet_files:
            st.multiselect(
                "Select code snippets:",
                available_snippet_files,
                default=st.session_state.selected_snippet_files,
                key="snippet_files_select"
            )
            # Update selected files when widget value changes
            st.session_state.selected_snippet_files = st.session_state.snippet_files_select
        else:
            st.info("No code snippets available. Please paste code in the Code Snippet Documentation tab.")
    
    with source_tabs[3]:
        # Combine all available files
        all_files = list(set(available_project_files + available_uploaded_files + available_snippet_files))
        
        # Filter all selected files to only include available files
        all_selected = [f for f in 
            list(set(
                st.session_state.selected_project_files + 
                st.session_state.selected_uploaded_files +
                st.session_state.selected_snippet_files
            )) 
            if f in all_files
        ]
        
        if all_files:
            st.multiselect(
                "Select from all files:",
                all_files,
                default=all_selected,
                key="all_files_select"
            )
            # This selection overrides individual selections
            selected_all = st.session_state.all_files_select
            
            # Update project and uploaded file selections based on all selection
            st.session_state.selected_project_files = [f for f in selected_all if f in available_project_files]
            st.session_state.selected_uploaded_files = [f for f in selected_all if f in available_uploaded_files]
            st.session_state.selected_snippet_files = [f for f in selected_all if f in available_snippet_files]
        else:
            st.info("No files available. Please upload files, a project ZIP, or paste code snippets.")
    
    # Get all selected files across all sources
    selected_files = list(set(
        st.session_state.selected_project_files + 
        st.session_state.selected_uploaded_files +
        st.session_state.selected_snippet_files
    ))
    
    # Check if files are selected
    if not selected_files:
        st.warning("Please select at least one file to enable the chatbot.")
        st.info("Use the multi-select dropdowns above to choose which files to include in the conversation.")
        
        # Disable chat functionality when no files are selected
        st.chat_input("Select files above to enable chat...", disabled=True)
        return
    
    # Display selected context
    st.success(f"Assistant will use context from: {', '.join(selected_files)}")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    user_question = st.chat_input("Ask a question about your code...")
    
    if user_question:
        # Add user question to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        st.chat_message("user").write(user_question)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing code..."):
                # Combine chunks from all sources for selected files
                all_chunks = st.session_state.project_chunks + st.session_state.file_chunks + st.session_state.snippet_chunks
                response = query_with_context(user_question, all_chunks, selected_files)
                st.write(response)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Option to clear chat history
    if st.session_state.chat_history and st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

def query_with_context(question, chunks, selected_files=None):
    """
    Query the LLM with context from selected files.
    
    Args:
        question: User question
        chunks: List of all code chunks
        selected_files: List of files to use as context
        
    Returns:
        LLM response
    """
    # Filter chunks by selected files if provided
    if selected_files:
        filtered_chunks = [chunk for chunk in chunks if chunk['metadata']['file'] in selected_files]
    else:
        # This case shouldn't occur with the UI restrictions
        return "Please select at least one file to provide context for the conversation."
    
    if not filtered_chunks:
        return "No code context available. The selected files don't contain valid code chunks."
    
    # Prepare context from filtered chunks
    context = ""
    for chunk in filtered_chunks:
        context += f"File: {chunk['metadata']['file']}\n"
        context += f"Type: {chunk['metadata']['type']}\n"
        context += f"Name: {chunk['metadata']['name']}\n"
        context += f"Code:\n{chunk['code']}\n\n"
    
    # Create the prompt with the question and context
    prompt = f"""
I'll provide you with some Python code and a question about it. Please answer the question using the code context.

CODE CONTEXT:
{context}

QUESTION:
{question}

Please provide a clear, professional answer based on the code context. If the answer isn't clear from the provided code, say so.
"""
    
    # Call the LLM
    response = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a professional software engineer who provides technically precise answers about code."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content