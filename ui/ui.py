import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from streamlit_cookies_controller import CookieController
from uuid import uuid4

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Research Assistant",
    page_icon="📚",
    layout="wide",
)

cookie_controller = CookieController()
session_id = cookie_controller.get("session_id")
if "first_run" in st.session_state and session_id == None:
    session_id = uuid4().hex
    cookie_controller.set("session_id", session_id)
print("session_id", session_id)
requests_session = requests.Session()
requests_session.headers.update(
    { "session-id": session_id }
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "documents" not in st.session_state:
    st.session_state.documents = []

def fetch_documents() -> List[str]:
    """
    Get the list of names of the documents
    """
    try:
        response = requests_session.get(f"{API_URL}/documents")
        if response.status_code == 200:
            return response.json()["documents"]
        else:
            st.error(f"Error fetching documents: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def upload_document(file) -> bool:
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file, "application/pdf")}
        response = requests_session.post(f"{API_URL}/documents", files=files)
        if response.status_code == 201:
            st.success("Document uploaded successfully!")
            return True
        else:
            st.error(f"Error uploading document: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False


def delete_all_documents() -> bool:
    """Delete all documents from the collection."""
    try:
        response = requests_session.delete(f"{API_URL}/documents")
        if response.status_code == 200:
            st.success("All documents deleted successfully!")
            return True
        else:
            st.error(f"Error deleting documents: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return False


def get_messages():
    response = requests_session.get(f"{API_URL}/messages")
    if response.status_code == 200:
        data = response.json()
        print("DATA", data)
        return [{"content": d["content"], "type": d["type"]} for d in data["messages"]]


def send_message(message: str) -> Optional[Dict[str, Any]]:
    """Send a message to the API and get a response."""
    try:
        payload = {
            "message": message,
        }

        response = requests_session.post(f"{API_URL}/chat", json=payload)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error(f"Error sending message: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None


def display_chat_message(message: Dict[str, Any]):
    """Display a chat message with the appropriate styling."""
    if message["type"] == "human":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

def clear_conversation():
    response = requests_session.delete(f"{API_URL}/messages")
    if response.status_code == 200:
        st.session_state.messages = []

if not "documents_fetched" in st.session_state and "first_run" in st.session_state:
    st.session_state.documents_fetched = True
    st.session_state.documents = fetch_documents()

def main():
    """Main function to run the Streamlit app."""
    st.title("📚 Research Assistant")
    with st.sidebar:
        st.header("Document Management")
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key=f"file_uploader_{st.session_state.get('upload_key', 0)}")
        if uploaded_file is not None:
            if st.button("Upload"):
                with st.spinner("Uploading and processing document..."):
                    success = upload_document(uploaded_file)
                    if success:
                        st.session_state.documents = fetch_documents()
                        st.session_state.upload_key = st.session_state.get('upload_key', 0) + 1
                        st.rerun()

        st.subheader("Available Documents")
        if st.button("Refresh Documents", use_container_width=True):
            with st.spinner("Fetching documents..."):
                st.session_state.documents = fetch_documents()

        if st.session_state.documents:
            for doc in st.session_state.documents:
                st.text(f"• {doc}")
        else:
            st.info("No documents available. Upload a PDF to get started.")

        st.subheader("Delete Documents")
        if st.button("Delete All Documents", type="primary", use_container_width=True):
            if st.session_state.documents:
                with st.spinner("Deleting all documents..."):
                    success = delete_all_documents()
                    if success:
                        st.session_state.documents = []
                        st.rerun()
            else:
                st.warning("No documents to delete.")

        st.subheader("Conversation")
        if st.button("Start New Conversation", use_container_width=True):
            clear_conversation()
            st.rerun()

    st.header("Chat with your Documents")

    for message in get_messages():
        display_chat_message(message)

    if prompt := st.chat_input("Ask a question about your documents..."):
        user_message = {"type": "human", "content": prompt}
        display_chat_message(user_message)

        with st.spinner("Thinking..."):
            response = send_message(prompt)
            print("response", response)
            display_chat_message(response)

    if not "first_run" in st.session_state:
        st.session_state.first_run = True

if __name__ == "__main__":
    main()
