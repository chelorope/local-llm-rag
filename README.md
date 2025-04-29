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

## Running in Docker

This section explains how to run the app using conteinarized services

### Installation

1. Clone this repository:

```
git clone <repository-url>
cd local-llm-rag
```

### Run

1. Start the application:

```
docker-compose up --build
```

## Running locally

This section explains how to run the API and UI components locally while using containerized MongoDB and ChromaDB.

### Installation

1. Install Poetry if you haven't already:

```bash
pip install poetry
```

2. Install API dependencies:

```bash
cd api
poetry install
cd ..
```

3. Install UI dependencies:

```bash
cd ui
poetry install
cd ..
```

4. Install Ollama and pull required models:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the required models
ollama pull llama2
ollama pull nomic-embed-text
```

### Run

1. Start MongoDB and ChromaDB containers:

```bash
docker-compose up mongodb chroma --build
```

2. Start the API server:

```bash
cd api
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

3. Start the UI server (in another terminal):

```bash
cd ui
poetry run streamlit run src/app.py
```

4. Access the application:
   - Web UI: <http://localhost:8501>
   - API Documentation: <http://localhost:8000/docs>

Note: Make sure you have Ollama installed and running locally with your desired models. The API will connect to Ollama on the default address (<http://localhost:11434>).

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
