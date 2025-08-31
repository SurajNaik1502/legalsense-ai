import os
import uuid
import json
import aiofiles
from typing import Optional, Dict, Any
from datetime import datetime
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
import logging

from models.schemas import DocumentInfo, LanguageCode

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.upload_dir = "uploads"
        self.processed_dir = "processed"
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure upload and processed directories exist"""
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    async def process_document(self, file, doc_id: str, language: str = "en") -> Dict[str, Any]:
        """Process uploaded document and extract text"""
        try:
            # Save uploaded file
            file_path = os.path.join(self.upload_dir, f"{doc_id}_{file.filename}")
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Extract text based on file type
            text_content = await self._extract_text(file_path, file.content_type)
            
            # Save processed content
            processed_path = os.path.join(self.processed_dir, f"{doc_id}.json")
            document_info = {
                "id": doc_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content),
                "uploaded_at": datetime.utcnow().isoformat(),
                "language": language,
                "processing_status": "completed",
                "text_content": text_content,
                "word_count": len(text_content.split()),
                "page_count": self._count_pages(text_content, file.content_type)
            }
            
            async with aiofiles.open(processed_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(document_info, ensure_ascii=False, indent=2))
            
            return document_info
            
        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {str(e)}")
            raise
    
    async def _extract_text(self, file_path: str, content_type: str) -> str:
        """Extract text from different file types"""
        try:
            if content_type == "application/pdf":
                return await self._extract_from_pdf(file_path)
            elif content_type == "application/msword":
                return await self._extract_from_doc(file_path)
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                return await self._extract_from_docx(file_path)
            elif content_type == "text/plain":
                return await self._extract_from_text(file_path)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2 and OCR if needed"""
        try:
            # Try PyPDF2 first
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += page_text + "\n"
            
            # If no text extracted, try OCR
            if not text.strip():
                text = await self._ocr_pdf(file_path)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting from PDF: {str(e)}")
            # Fallback to OCR
            return await self._ocr_pdf(file_path)
    
    async def _ocr_pdf(self, file_path: str) -> str:
        """Extract text from PDF using OCR"""
        try:
            # Convert PDF to images
            images = convert_from_path(file_path)
            text = ""
            
            for i, image in enumerate(images):
                # Extract text using OCR
                page_text = pytesseract.image_to_string(image)
                text += f"Page {i+1}:\n{page_text}\n\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error in OCR: {str(e)}")
            raise
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting from DOCX: {str(e)}")
            raise
    
    async def _extract_from_doc(self, file_path: str) -> str:
        """Extract text from DOC file (basic implementation)"""
        # For .doc files, we'll need additional libraries like python-docx2txt
        # For now, return a placeholder
        return f"DOC file content from {file_path} - OCR processing required"
    
    async def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            raise
    
    def _count_pages(self, text: str, content_type: str) -> int:
        """Estimate page count based on content"""
        if content_type == "application/pdf":
            # Rough estimate: 500 words per page
            word_count = len(text.split())
            return max(1, word_count // 500)
        else:
            # For other formats, estimate based on line breaks
            lines = text.count('\n')
            return max(1, lines // 50)
    
    async def get_document_content(self, doc_id: str) -> Optional[str]:
        """Get processed document content"""
        try:
            processed_path = os.path.join(self.processed_dir, f"{doc_id}.json")
            if not os.path.exists(processed_path):
                return None
            
            async with aiofiles.open(processed_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                document_info = json.loads(content)
                return document_info.get("text_content", "")
                
        except Exception as e:
            logger.error(f"Error getting document content: {str(e)}")
            return None
    
    async def get_document_info(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document information"""
        try:
            processed_path = os.path.join(self.processed_dir, f"{doc_id}.json")
            if not os.path.exists(processed_path):
                return None
            
            async with aiofiles.open(processed_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            return None
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document and its processed data"""
        try:
            # Delete processed file
            processed_path = os.path.join(self.processed_dir, f"{doc_id}.json")
            if os.path.exists(processed_path):
                os.remove(processed_path)
            
            # Delete uploaded file (find by doc_id prefix)
            for filename in os.listdir(self.upload_dir):
                if filename.startswith(doc_id):
                    os.remove(os.path.join(self.upload_dir, filename))
                    break
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
