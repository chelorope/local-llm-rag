import os
from dotenv import load_dotenv

load_dotenv()

DOCUMENTS_DIR = "documents"

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "documents_db")
MONGO_DOCUMENTS_COLLECTION_NAME = os.getenv("MONGO_DOCUMENTS_COLLECTION_NAME", "documents")
