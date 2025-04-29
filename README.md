# Local LLM RAG System

A local Retrieval-Augmented Generation (RAG) system that allows you to chat with your PDF documents using LLMs (Large Language Models) running on your machine through Ollama.

## Overview

This project implements a full-stack RAG system with the following components:

- **Web UI**: A Streamlit-based interface for uploading documents, managing your document library, and chatting with your documents
- **API Backend**: A FastAPI service that handles document processing, vector storage, and LLM interactions
- **Database Storage**: MongoDB for storing documents and conversation history
- **Vector Storage**: ChromaDB for storing and searching document embeddings
- **LLM Integration**: Uses Ollama to run local language models for embeddings and completion

## Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Ollama](https://ollama.ai/) installed on your machine
- Required Ollama models:
  - `llama3.2` (for chat completions)
  - `nomic-embed-text` (for embeddings)

## Installation

1. Clone this repository:

```
git clone <repository-url>
cd local-llm-rag
```

2. Install and start Ollama from [ollama.ai](https://ollama.ai/)

3. Pull the required models:

```
ollama pull llama3.2
ollama pull nomic-embed-text
```

4. Start the application:

```
docker-compose up --build
```

## Usage

1. Open your browser and navigate to <http://localhost:8501> to access the UI

2. Upload PDF documents using the file uploader in the sidebar

3. Ask questions about your documents in the chat interface

4. Start a new conversation or delete documents as needed using the sidebar controls

## Project Structure

- `api/`: FastAPI backend service

  - `src/`: Source code for the API components
  - `documents/`: Storage location for uploaded PDFs
  - `config/`: Configuration settings
  - `chroma_langchain_db/`: Vector database storage

- `ui/`: Streamlit front-end application

## Customization

You can modify the default LLM settings in the `api/config/settings.py` file:

- Change the embedding model: `embedding_model`
- Change the LLM model: `llm_model`
- Adjust chunk size and overlap for document processing

## Troubleshooting

- Make sure Ollama is running and the required models are installed
- Check Docker container logs for any startup errors
- Ensure ports 8000 (API), 8501 (UI), 27017 (MongoDB), and 3020 (ChromaDB) are available

## License

[License information]
