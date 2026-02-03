import os
from typing import List, Dict, Any
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException
import PyPDF2
import pdfplumber
from app.services.supabase_service import get_supabase_admin


class FileService:
    """Service for handling file uploads and parsing"""

    # Allowed file types
    ALLOWED_TXT_EXTENSIONS = {".txt"}
    ALLOWED_PDF_EXTENSIONS = {".pdf"}

    # Upload directories
    UPLOAD_DIR = Path("uploads")
    CHARACTERS_DIR = UPLOAD_DIR / "characters"
    SOURCES_DIR = UPLOAD_DIR / "sources"

    def __init__(self):
        """Initialize file service and create directories"""
        self.CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)
        self.SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    async def save_upload_file(self, file: UploadFile, directory: Path) -> str:
        """Save uploaded file to disk"""
        file_path = directory / file.filename

        # Validate file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in self.ALLOWED_TXT_EXTENSIONS | self.ALLOWED_PDF_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {self.ALLOWED_TXT_EXTENSIONS | self.ALLOWED_PDF_EXTENSIONS}"
            )

        # Save file
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        return str(file_path)

    async def upload_to_supabase(
        self,
        file_path: str,
        bucket: str,
        filename: str
    ) -> str:
        """Upload file to Supabase Storage"""
        supabase = get_supabase_admin()

        try:
            with open(file_path, "rb") as f:
                supabase.storage.from_(bucket).upload(filename, f)
            # Return public URL
            return f"{supabase.storage.from_(bucket).get_public_url(filename)}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    def parse_character_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse character database TXT file"""
        characters = []
        current_character = {}

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    if current_character:
                        characters.append(current_character)
                        current_character = {}
                    continue

                if line.startswith("CHARACTER:"):
                    if current_character:
                        characters.append(current_character)
                    current_character = {"name": line.split(":", 1)[1].strip()}
                elif ":" in line and current_character:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key == "name":
                        current_character["name"] = value
                    elif key == "traits":
                        current_character["traits"] = [t.strip() for t in value.split(",")]
                    elif key == "style":
                        current_character["style"] = value
                    elif key == "expressions":
                        current_character["expressions"] = [e.strip() for e in value.split(",")]
                    elif key == "poses":
                        current_character["poses"] = [p.strip() for p in value.split(",")]

            # Don't forget the last character
            if current_character:
                characters.append(current_character)

        return characters

    def parse_pdf_file(self, file_path: str) -> str:
        """Parse PDF file and extract text content"""
        text = ""

        try:
            # Try pdfplumber first (better extraction)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            # Fallback to PyPDF2
            try:
                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse PDF: {str(e)}"
                )

        return text.strip()

    def parse_source_file(self, file_path: str) -> str:
        """Parse source material file (PDF or TXT)"""
        ext = Path(file_path).suffix.lower()

        if ext in self.ALLOWED_TXT_EXTENSIONS:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext in self.ALLOWED_PDF_EXTENSIONS:
            return self.parse_pdf_file(file_path)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format"
            )

    async def cleanup_file(self, file_path: str):
        """Remove temporary file"""
        try:
            os.remove(file_path)
        except Exception:
            pass


# Singleton instance
file_service = FileService()
