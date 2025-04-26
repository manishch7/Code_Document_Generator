import streamlit as st

# First Streamlit command MUST be set_page_config
st.set_page_config(page_title="Code Documentation Assistant", layout="wide")

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
st.title("📄 Code Documentation Assistant")

# Initialize session state variables
if 'processed_chunks' not in st.session_state:
    st.session_state.processed_chunks = []

# Add separate chunk storages for different sources
if 'project_chunks' not in st.session_state:
    st.session_state.project_chunks = []
if 'file_chunks' not in st.session_state:
    st.session_state.file_chunks = []
if 'snippet_chunks' not in st.session_state:
    st.session_state.snippet_chunks = []

# Initialize documentation storage
if 'file_documentation' not in st.session_state:
    st.session_state.file_documentation = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize file selection variables
if 'selected_project_files' not in st.session_state:
    st.session_state.selected_project_files = []
if 'selected_uploaded_files' not in st.session_state:
    st.session_state.selected_uploaded_files = []
if 'selected_snippet_files' not in st.session_state:
    st.session_state.selected_snippet_files = []
    
# Initialize file list variables
if 'available_files' not in st.session_state:
    st.session_state.available_files = []
if 'project_files' not in st.session_state:
    st.session_state.project_files = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'snippet_files' not in st.session_state:
    st.session_state.snippet_files = []

# Project documentation variables
if 'project_summary' not in st.session_state:
    st.session_state.project_summary = None
if 'project_documentation' not in st.session_state:
    st.session_state.project_documentation = None

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