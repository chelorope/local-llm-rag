import uuid
import os
from pathlib import Path

class FileHandler:
    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file_content: bytes, extension: str = "pdf") -> Path:
        file_path = self.documents_dir / f"{uuid.uuid4().hex}.{extension}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
            
        return file_path
    
    def delete_file(self, file_path: Path) -> bool:
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def delete_files(self, file_paths: list[Path]) -> list[Path]:
        deleted_files = []
        for file_path in file_paths:
            if self.delete_file(file_path):
                deleted_files.append(file_path)
        return deleted_files 