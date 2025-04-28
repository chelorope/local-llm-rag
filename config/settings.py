import os
from dotenv import load_dotenv

load_dotenv()

DOCUMENTS_DIR = "tmp/documents"

os.makedirs(DOCUMENTS_DIR, exist_ok=True)