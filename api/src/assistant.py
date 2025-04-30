from langchain_ollama import ChatOllama
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.runnable import Runnable, RunnableLambda
from typing import Optional, List
from src.vector_store import VectorStore
from langchain_mongodb import MongoDBChatMessageHistory
from langchain.schema import AIMessage, HumanMessage, BaseMessage
from config.settings import settings
import os

class PDFAssistant:
    def __init__(self, persist_directory: str, model_name: str, 
                 mongo_uri: str, mongo_db_name: str, mongo_message_history_collection: str):
        """Initialize the PDF Assistant with vector store and model configuration."""
        self.vector_store = VectorStore(persist_directory=persist_directory)
        self.model = ChatOllama(
            model=model_name,
            base_url=f"http://{settings.ollama_host}:{settings.ollama_port}"
        )
        self.mongo_uri = mongo_uri
        self.mongo_db_name = mongo_db_name
        self.mongo_message_history_collection = mongo_message_history_collection

    def _get_message_history_store(self, session_id: Optional[str] = None) -> MongoDBChatMessageHistory:
        return MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=self.mongo_uri,
            database_name=self.mongo_db_name,
            collection_name=self.mongo_message_history_collection
        )
        
    async def _get_context(self, inputs):
        """Retrieve relevant context from vector store based on question."""
        question = inputs["question"]
        session_id = inputs.get("session_id")
        
        docs = await self.vector_store.search_documents(question, session_id=session_id)
        
        if not docs:
            context = "No documents found in your current session. Please upload relevant PDF documents first."
        else:
            context = "\n\n".join(doc.page_content for doc in docs)
        
        print(f"\n\n\n\n\nQUESTION: {question}\n\n\n\n\nCONTEXT: {context}\n\n\n\n\n")
        return {
            "context": context,
            "question": question
        }

    def _create_rag_chain(self) -> Runnable:
        """Create and return the RAG chain for question answering."""
        prompt = ChatPromptTemplate.from_template("""
            <|begin_of_text|><|start_header_id|>system<|end_header_id|> 
            You are an assistant for question-answering tasks. Use the following pieces 
            of retrieved context to answer the question. 
            If you can't answer the question based on the context, just say that you don't know. 
            Use three sentences maximum and keep the answer concise 
            <|eot_id|><|start_header_id|>user<|end_header_id|> 
                                                  
            Question: {question} 
                                                  
            Context: {context} 
                                                  
            Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>
        """)
        
        return (
            RunnableLambda(self._get_context)
            | prompt
            | self.model
        )
        
    async def ask(self, question: str, session_id: Optional[str] = None) -> AIMessage:
        """Process a question and return an answer using the RAG chain."""
        message_history = self._get_message_history_store(session_id)
        message_history.add_message(HumanMessage(content=question))
        
        chain = self._create_rag_chain()
        response = await chain.ainvoke({"question": question, "session_id": session_id})
        assistant_message = AIMessage(content=response.content)
        message_history.add_message(assistant_message)
        
        return assistant_message
    
    def get_message_history(self, session_id: str) -> List[BaseMessage]:
        message_history = self._get_message_history_store(session_id)
        return message_history.messages
    
    def delete_message_history(self, session_id: str) -> None:
        message_history = self._get_message_history_store(session_id)
        message_history.clear()