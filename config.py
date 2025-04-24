import configparser
import os
from pathlib import Path
import sys

# Try to load credentials from config.ini
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
        
except KeyError as e:
    print(f"ERROR: Missing required configuration in config.ini: {e}")
    print("Please ensure your config.ini has [openai] and [pinecone] sections with the required keys.")
    sys.exit(1)