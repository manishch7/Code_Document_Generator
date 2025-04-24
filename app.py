import streamlit as st
import tempfile
import os
from src.preprocessing.chunker import extract_chunks
from src.embeddings.store import upsert_chunks
from src.generation.generate import generate_documentation
import openai
from config import OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
LLM_MODEL = "gpt-4o-mini-2024-07-18"

st.set_page_config(page_title="Code Documentation Assistant", layout="wide")
st.title("📄 Code Documentation Assistant")

# Initialize session state
if 'processed_chunks' not in st.session_state:
    st.session_state.processed_chunks = []
if 'documentation_results' not in st.session_state:
    st.session_state.documentation_results = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to query the LLM with context from the uploaded code
def query_with_context(question, chunks):
    # Prepare context from all chunks
    context = ""
    for chunk in chunks:
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

Please provide a clear, concise answer based on the code context. If the answer isn't clear from the provided code, say so.
"""
    
    # Call the LLM
    response = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions about code."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

# Create tabs for the main interface
doc_tab, chat_tab = st.tabs(["Documentation Generator", "Code Chatbot"])

with doc_tab:
    # Sidebar: Upload files for indexing
    st.sidebar.header("Upload Python Files")
    uploaded_files = st.sidebar.file_uploader("Upload Python files", accept_multiple_files=True, type=["py"])
    
    # Process files
    if uploaded_files and st.sidebar.button("Process Files"):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files to temp directory
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            # Extract and index chunks
            with st.sidebar.status("Processing files..."):
                chunks = extract_chunks(temp_dir)
                
                if chunks:
                    # Store chunks in session state
                    st.session_state.processed_chunks = chunks
                    
                    # Upsert chunks to vector database
                    upsert_chunks(chunks)
                    st.sidebar.success(f"Processed {len(chunks)} code chunks from {len(uploaded_files)} files.")
                else:
                    st.sidebar.error("No valid code chunks found in the uploaded files.")
    
    # Main area: Generate docs for each chunk
    if st.session_state.processed_chunks:
        st.header("Generate Documentation")
        
        if st.button("Generate Documentation for All Code"):
            with st.status("Generating documentation..."):
                # Group chunks by file for better organization
                files = {}
                for chunk in st.session_state.processed_chunks:
                    file_name = chunk['metadata']['file']
                    if file_name not in files:
                        files[file_name] = []
                    files[file_name].append(chunk)
                
                # Generate documentation for each file's chunks
                for file_name, file_chunks in files.items():
                    st.subheader(f"File: {file_name}")
                    
                    for i, chunk in enumerate(file_chunks):
                        chunk_id = chunk['id']
                        
                        # Generate documentation for this chunk
                        docs = generate_documentation(chunk['code'], chunk['metadata'])
                        
                        # Store documentation in session state
                        st.session_state.documentation_results[chunk_id] = {
                            'code': chunk['code'],
                            'docs': docs,
                            'metadata': chunk['metadata']
                        }
                        
                        # Create tabs for code and documentation
                        code_tab, docs_tab = st.tabs(["Code", "Documentation"])
                        
                        with code_tab:
                            st.code(chunk['code'], language="python")
                        
                        with docs_tab:
                            # Show documentation with download button
                            st.markdown(docs)
                            st.download_button(
                                label="Download Documentation",
                                data=docs,
                                file_name=f"{chunk['metadata']['name']}_documentation.pdf",
                                mime="text/markdown",
                                key=f"download_{file_name}_{i}"
                            )
                        
                        st.divider()
        
        # Add option to view previously generated documentation
        if st.session_state.documentation_results:
            st.header("Access Generated Documentation")
            
            # Create selectbox for choosing documentation
            chunk_options = []
            for chunk_id, result in st.session_state.documentation_results.items():
                chunk_options.append(f"{result['metadata']['file']} - {result['metadata']['name']} ({result['metadata']['type']})")
            
            selected_chunk = st.selectbox("Select documentation to view", chunk_options)
            
            if selected_chunk:
                # Extract chunk ID from selection
                selected_index = chunk_options.index(selected_chunk)
                selected_chunk_id = list(st.session_state.documentation_results.keys())[selected_index]
                result = st.session_state.documentation_results[selected_chunk_id]
                
                # Show documentation in expandable section
                with st.expander("Documentation", expanded=True):
                    st.markdown(result['docs'])
                    st.download_button(
                        label="Download Documentation",
                        data=result['docs'],
                        file_name=f"{result['metadata']['name']}_documentation.pdf",
                        mime="text/markdown",
                        key=f"download_viewer_{selected_chunk_id}"
                    )
    else:
        # No files processed yet
        st.info("Upload Python files and click 'Process Files' to get started.")
    
    # Option to paste code directly
    st.header("Or Paste Code Directly")
    user_code = st.text_area("Paste a function or class here:")
    if st.button("Generate Docs for Pasted Code") and user_code.strip():
        metadata = {'file': 'input', 'name': 'snippet', 'type': 'FunctionDef'}
        docs = generate_documentation(user_code, metadata)
        
        # Display documentation with download option
        st.markdown(docs)
        st.download_button(
            label="Download Documentation",
            data=docs,
            file_name="pasted_code_documentation.pdf",
            mime="text/markdown",
            key="download_pasted_code"
        )

with chat_tab:
    st.header("Ask Questions About Your Code")
    
    if not st.session_state.processed_chunks:
        st.warning("Please upload and process files in the Documentation Generator tab first.")
    else:
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
                with st.spinner("Thinking..."):
                    response = query_with_context(user_question, st.session_state.processed_chunks)
                    st.write(response)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Option to clear chat history
        if st.session_state.chat_history and st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()