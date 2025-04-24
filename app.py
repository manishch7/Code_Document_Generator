import streamlit as st
import openai
from config import OPENAI_API_KEY

# Import UI modules
from src.ui.project_tab import render_project_tab
from src.ui.file_tab import render_file_tab
from src.ui.snippet_tab import render_snippet_tab
from src.ui.chat_tab import render_chat_tab

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Set up the Streamlit page
st.set_page_config(page_title="Code Documentation Assistant", layout="wide")
st.title("📄 Professional Code Documentation Assistant")

# Initialize session state variables
if 'processed_chunks' not in st.session_state:
    st.session_state.processed_chunks = []
if 'file_documentation' not in st.session_state:
    st.session_state.file_documentation = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_files_for_chat' not in st.session_state:
    st.session_state.selected_files_for_chat = []
if 'available_files' not in st.session_state:
    st.session_state.available_files = []
if 'project_summary' not in st.session_state:
    st.session_state.project_summary = None
if 'project_documentation' not in st.session_state:
    st.session_state.project_documentation = None
if 'pasted_code' not in st.session_state:
    st.session_state.pasted_code = None
if 'pasted_code_chunk' not in st.session_state:
    st.session_state.pasted_code_chunk = None

# Create tabs for the main interface
project_tab, doc_tab, code_paste_tab, chat_tab = st.tabs([
    "Project Documentation", 
    "File Documentation", 
    "Code Snippet Documentation", 
    "Code Chatbot"
])

# Render each tab with its own module
with project_tab:
    render_project_tab()

with doc_tab:
    render_file_tab()

with code_paste_tab:
    render_snippet_tab()

with chat_tab:
    render_chat_tab()