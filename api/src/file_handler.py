import uuid
import os
import aiofiles
from pathlib import Path
from typing import List

class FileHandler:
    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file_content: bytes, extension: str = "pdf") -> Path:
        file_path = self.documents_dir / f"{uuid.uuid4().hex}.{extension}"
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
            
        return file_path
    
    async def delete_file(self, file_path: Path) -> bool:
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception:
                return False
        return False
    
    async def delete_files(self, file_paths: List[Path]) -> List[Path]:
        deleted_files = []
        for file_path in file_paths:
            if await self.delete_file(file_path):
                deleted_files.append(file_path)
        return deleted_files 