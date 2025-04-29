from langchain_core.output_parsers import JsonOutputParser
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.runnable import Runnable, RunnableLambda
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from src.vector_store import VectorStore
from langchain_mongodb import MongoDBChatMessageHistory
from config.settings import MONGO_URI, MONGO_DB_NAME
from langchain.schema import AIMessage, HumanMessage, BaseMessage

class PDFAssistant:
    def __init__(self, persist_directory="./chroma_langchain_db", model_name="llama3.2"):
        """Initialize the PDF Assistant with vector store and model configuration."""
        self.vector_store = VectorStore(persist_directory=persist_directory)
        self.model_name = model_name
        
    def _get_context(self, inputs):
        """Retrieve relevant context from vector store based on question."""
        question = inputs["question"]
        session_id = inputs.get("session_id")
        
        # Search documents with session_id filter
        docs = self.vector_store.search_documents(question, session_id=session_id)
        
        if not docs:
            print(f"No documents found for session: {session_id}")
            context = "No documents found in your current session. Please upload relevant PDF documents first."
        else:
            context = "\n\n".join(doc.page_content for doc in docs)
        
        print(f"\n\n\n\n\nQUESTION: {question}\n\n\n\n\nCONTEXT: {context}\n\n\n\n\n")
        return {
            "context": context,
            "question": question
        }

    def _get_rag_chain(self) -> Runnable:
        """Create and return the RAG chain for question answering."""
        prompt = ChatPromptTemplate.from_template("""
            <|begin_of_text|><|start_header_id|>system<|end_header_id|> 
            You are an assistant for question-answering tasks. Use the following pieces 
            of retrieved context to answer the question. 
            If you don't know the answer, just say that you don't know. 
            Use three sentences maximum and keep the answer concise 
            <|eot_id|><|start_header_id|>user<|end_header_id|> 
                                                  
            Question: {question} 
                                                  
            Context: {context} 
                                                  
            Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """)
        
        return (
            RunnableLambda(self._get_context)
            | prompt
            | ChatOllama(model=self.model_name)
        )
        
    def ask(self, question: str, session_id: Optional[str] = None) -> str:
        """Process a question and return an answer using the RAG chain."""
        message_history = MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=MONGO_URI,
            database_name=MONGO_DB_NAME,
            collection_name="message_history"
        )
        message_history.add_message(HumanMessage(content=question))
        chain = self._get_rag_chain()
        response = chain.invoke({"question": question, "session_id": session_id}).content
        assistant_message = AIMessage(content=response)
        message_history.add_message(assistant_message)
        return assistant_message
    
    def get_message_history(self, session_id: str) -> list[BaseMessage]:
        message_history = MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=MONGO_URI,
            database_name=MONGO_DB_NAME,
            collection_name="message_history"
        )
        return message_history.messages
    
    def delete_message_history(self, session_id: str):
        message_history = MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=MONGO_URI,
            database_name=MONGO_DB_NAME,
            collection_name="message_history"
        )
        message_history.clear()