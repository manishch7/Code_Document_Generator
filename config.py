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
    OPENAI_API_KEY = st.secrets["openai"]["api_key"]
    PINECONE_API_KEY = st.secrets["pinecone"]["api_key"]
    PINECONE_INDEX = st.secrets["pinecone"]["index"]
    print("Successfully loaded credentials from Streamlit secrets")
    using_secrets = True
except (ImportError, FileNotFoundError, KeyError) as e:
    print(f"Could not load from Streamlit secrets: {e}")
    using_secrets = False

# Only try to use config.ini if secrets didn't work
if not using_secrets:
    # Use config.ini approach for local development
    cfg = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config.ini"
    
    # Check if config.ini exists
    if not config_path.exists():
        print(f"WARNING: config.ini not found at {config_path}")
        print("Setting empty API keys - application will not function correctly")
        OPENAI_API_KEY = ""
        PINECONE_API_KEY = ""
        PINECONE_INDEX = ""
    else:
        # Read the config file
        cfg.read(config_path)
        
        try:
            # OpenAI
            OPENAI_API_KEY = cfg["openai"]["api_key"]
            if OPENAI_API_KEY == "your_openai_api_key_here":
                print("ERROR: Please set your actual OpenAI API key in config.ini")
                
            # Pinecone
            PINECONE_API_KEY = cfg["pinecone"]["api_key"]
            if PINECONE_API_KEY == "your_pinecone_api_key_here":
                print("ERROR: Please set your actual Pinecone API key in config.ini")
                
            PINECONE_INDEX = cfg["pinecone"]["index"]
            if PINECONE_INDEX == "your_pinecone_index_name_here":
                print("ERROR: Please set your actual Pinecone index name in config.ini")
                
            print("Successfully loaded credentials from config.ini")
            
        except KeyError as e:
            print(f"ERROR: Missing required configuration in config.ini: {e}")
            print("Setting empty API keys - application will not function correctly")
            OPENAI_API_KEY = ""
            PINECONE_API_KEY = ""
            PINECONE_INDEX = ""