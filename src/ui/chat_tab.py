import streamlit as st
import openai
from config import OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
LLM_MODEL = "gpt-4o-mini-2024-07-18"

def render_chat_tab():
    """Render the Code Chatbot tab UI and functionality."""
    st.header("Code Expert Assistant")
    
    if not st.session_state.processed_chunks:
        st.warning("Please upload and process files in the File Documentation tab or process a project ZIP first.")
        return
    
    # Context selection
    st.subheader("Select Context Type")
    context_type = st.selectbox(
        "Choose context type for the conversation:",
        ["Entire Project", "Selected Files", "Pasted Code"],
        index=1  # Default to Selected Files
    )
    
    if context_type == "Entire Project":
        # Use all available files for context
        selected_files = st.session_state.available_files
        st.success(f"Using all {len(selected_files)} files from the project as context")
        
    elif context_type == "Selected Files":
        # File selection for context
        available_files = st.session_state.available_files
        selected_files = st.multiselect(
            "Select files to include in the conversation:",
            available_files,
            default=st.session_state.selected_files_for_chat
        )
        
        # Update selected files in session state
        st.session_state.selected_files_for_chat = selected_files
        
        # Check if files are selected
        if not selected_files:
            st.warning("Please select at least one file to enable the chatbot.")
            st.info("Use the multi-select dropdown above to choose which files to include in the conversation.")
            
            # Disable chat functionality when no files are selected
            st.chat_input("Select files above to enable chat...", disabled=True)
            return
            
        st.success(f"Assistant will use context from: {', '.join(selected_files)}")
        
    else:  # Pasted Code
        # Allow user to paste code for context
        user_code = st.text_area(
            "Paste your code here for context:", 
            height=200,
            placeholder="Paste Python code to use as context for the conversation..."
        )
        
        if not user_code.strip():
            st.warning("Please paste some code to enable the chatbot.")
            st.chat_input("Paste code above to enable chat...", disabled=True)
            return
            
        # Create a temporary chunk for the pasted code
        if user_code.strip():
            # Only update if there's a change to avoid recreating on every rerun
            if 'pasted_code' not in st.session_state or st.session_state.pasted_code != user_code:
                st.session_state.pasted_code = user_code
                
                # Infer code type
                from src.core.documentation.code_analyzer import infer_code_type
                code_type, code_name = infer_code_type(user_code)
                
                # Create a chunk for the pasted code
                st.session_state.pasted_code_chunk = [{
                    'id': 'pasted_code',
                    'code': user_code,
                    'metadata': {
                        'file': 'pasted_code.py',
                        'name': code_name,
                        'type': code_type
                    }
                }]
                
            selected_files = ['pasted_code.py']  # Using the pasted code
            st.success("Using pasted code as context")
    
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
                # Determine which chunks to use based on context type
                if context_type == "Pasted Code":
                    chunks = st.session_state.pasted_code_chunk
                else:
                    chunks = st.session_state.processed_chunks
                
                response = query_with_context(user_question, chunks, selected_files)
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