# Code Documentation Assistant

A professional code documentation tool that uses Retrieval-Augmented Generation (RAG) to create context-aware documentation for Python codebases.

## Overview

The Code Documentation Assistant is an intelligent documentation generator that analyzes your Python code within its broader context. Unlike traditional documentation tools that generate isolated docstrings, this system enhances documentation by:

- Retrieving and analyzing related code from across your project
- Understanding relationships between functions, classes, and modules
- Providing comprehensive documentation with examples and edge cases
- Answering natural language questions about your codebase

## Features

- **Project Documentation**: Upload an entire project ZIP to generate comprehensive documentation
- **File Documentation**: Upload individual Python files for targeted documentation
- **Code Snippet Documentation**: Generate documentation for pasted code snippets
- **Code Chatbot**: Ask natural language questions about your code with context-aware responses

## Architecture

The system uses a combination of:

- **OpenAI's GPT models** for natural language generation (specifically gpt-4o-mini)
- **Vector embeddings** (text-embedding-3-small) to represent code semantically
- **Pinecone vector database** for efficient retrieval of related code
- **Streamlit frontend** for intuitive user interaction

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key and index

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/code-documentation-assistant.git
   cd code-documentation-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a configuration file:
   ```bash
   cp config.ini.example config.ini
   ```

4. Edit `config.ini` with your API keys:
   ```ini
   [openai]
   api_key = your_openai_api_key_here

   [pinecone]
   api_key = your_pinecone_api_key_here
   index = your_pinecone_index_name_here
   ```

5. Launch the application:
   ```bash
   streamlit run app.py
   ```

## Usage

### Project Documentation

1. Navigate to the "Project Documentation" tab
2. Upload a ZIP file containing your Python project
3. Click "Process Project and Generate Documentation"
4. View and download the comprehensive project documentation

### File Documentation

1. Navigate to the "File Documentation" tab
2. Upload one or more Python files
3. Click "Process Files" followed by "Generate Documentation for All Files"
4. View and download documentation for each file

### Code Snippet Documentation

1. Navigate to the "Code Snippet Documentation" tab
2. Paste your Python code snippet
3. Click "Generate Professional Documentation"
4. View and download the generated documentation

### Code Chatbot

1. Process files or a project ZIP first
2. Navigate to the "Code Chatbot" tab
3. Select files to include in the conversation context
4. Ask questions about your code

## How It Works

1. **Code Chunking**: The system breaks down your code into logical chunks (functions, classes, methods)
2. **Embedding Generation**: Each code chunk is converted into a vector embedding
3. **Semantic Indexing**: Embeddings are stored in Pinecone for fast retrieval
4. **Context Retrieval**: When generating documentation, the system retrieves related code
5. **Enhanced Generation**: The LLM generates documentation using both the code and retrieved context

## Project Structure

```
code_documentation_assistant/
├── app.py                 # Main application entry point
├── config.py              # Configuration and API key management
├── config.ini             # Configuration file for API keys
├── requirements.txt       # Project dependencies
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── chunker.py     # Code chunking and analysis
│   │   ├── embeddings.py  # Embedding generation and storage
│   │   ├── retriever.py   # Semantic search functionality
│   │   └── documentation/ # Documentation generation components
│   │       ├── __init__.py
│   │       ├── code_analyzer.py     # Additional code analysis utilities
│   │       ├── context_retriever.py # Retrieves relevant code context
│   │       ├── generator.py         # Documentation generation logic
│   │       └── prompts.py           # LLM prompts for documentation
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── project_analyzer.py # Project structure analysis
│   │   └── zip_handler.py      # ZIP file processing
│   └── ui/
│       ├── __init__.py
│       ├── chat_tab.py    # Code chatbot UI
│       ├── file_tab.py    # File documentation UI
│       ├── project_tab.py # Project documentation UI
│       └── snippet_tab.py # Code snippet UI
```

## Workflow

1. **Initialization**: The system loads configuration from `config.py` and initializes connections to OpenAI and Pinecone
2. **User Interface**: Streamlit presents four main tabs for different documentation workflows
3. **Code Processing**:
   - For projects: ZIP files are extracted, files are parsed into chunks, and embedded in Pinecone
   - For individual files: Files are parsed, chunked, and embedded
   - For snippets: Code is analyzed, type-inferred, and documented
4. **Documentation Generation**: The system:
   - Retrieves relevant context from the vector database
   - Applies appropriate documentation prompts based on code type
   - Generates structured documentation with the LLM
5. **Interaction**: Users can ask questions about their code using the chatbot interface

## Dependencies

- openai
- pinecone
- python-dotenv
- tqdm
- streamlit
- numpy
- langchain

## Extensions and Customization

- **Custom Templates**: Modify the documentation templates in `prompts.py`
- **Additional Languages**: Extend the chunker to support other programming languages
- **Custom LLM**: Replace OpenAI with another model by modifying the API calls

## License

[MIT License](LICENSE)

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the web interface
- [OpenAI](https://openai.com/) for the language models
- [Pinecone](https://www.pinecone.io/) for vector search capabilities