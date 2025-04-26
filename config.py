import configparser
import os
from pathlib import Path
import sys

# Flag to determine if we're using Streamlit secrets or local config
using_secrets = False

# First try to get credentials from Streamlit secrets
try:
    import streamlit as st
    # Try accessing secrets
    st.secrets["test"]
    using_secrets = True
except (ImportError, FileNotFoundError, KeyError):
    # Fall back to config.ini for local development
    using_secrets = False

if using_secrets:
    try:
        # Get credentials from Streamlit secrets
        OPENAI_API_KEY = st.secrets["openai"]["api_key"]
        PINECONE_API_KEY = st.secrets["pinecone"]["api_key"]
        PINECONE_INDEX = st.secrets["pinecone"]["index"]
        print("Successfully loaded credentials from Streamlit secrets")
    except KeyError as e:
        print(f"ERROR: Missing required secret: {e}")
        print("Please configure secrets in Streamlit Cloud with [openai] and [pinecone] sections.")
        sys.exit(1)
else:
    # Use config.ini approach for local development
    cfg = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config.ini"
    
    # Check if config.ini exists
    if not config_path.exists():
        print(f"ERROR: config.ini not found at {config_path}")
        print("Please create a config.ini file with your API keys. See config.ini.example for format.")
        sys.exit(1)
    
    # Read the config file
    cfg.read(config_path)
    
    try:
        # OpenAI
        OPENAI_API_KEY = cfg["openai"]["api_key"]
        if OPENAI_API_KEY == "your_openai_api_key_here":
            print("ERROR: Please set your actual OpenAI API key in config.ini")
            sys.exit(1)
            
        # Pinecone
        PINECONE_API_KEY = cfg["pinecone"]["api_key"]
        if PINECONE_API_KEY == "your_pinecone_api_key_here":
            print("ERROR: Please set your actual Pinecone API key in config.ini")
            sys.exit(1)
            
        PINECONE_INDEX = cfg["pinecone"]["index"]
        if PINECONE_INDEX == "your_pinecone_index_name_here":
            print("ERROR: Please set your actual Pinecone index name in config.ini")
            sys.exit(1)
            
        print("Successfully loaded credentials from config.ini")
        
    except KeyError as e:
        print(f"ERROR: Missing required configuration in config.ini: {e}")
        print("Please ensure your config.ini has [openai] and [pinecone] sections with the required keys.")
        sys.exit(1)