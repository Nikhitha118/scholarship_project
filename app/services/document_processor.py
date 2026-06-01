import os
from typing import Dict, Optional
from PyPDF2 import PdfReader
from app.models.user import User
from app.models.document import Document

class DocumentProcessor:
    """Process and extract information from uploaded documents"""
    
    def __init__(self):
        self.upload_folder = 'app/static/uploads'
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        return ext in ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg']
    
    def extract_text_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF document"""
        try:
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def extract_user_info(self, user: User) -> Dict:
        """Extract additional user info from uploaded documents"""
        info = {}
        
        # Process documents to extract additional data
        for doc in user.documents:
            if doc.document_type == 'marksheet' and doc.file_path:
                text = self.extract_text_from_pdf(doc.file_path)
                # Simple extraction (you can enhance with LLM)
                if 'cgpa' in text.lower():
                    info['cgpa_extracted'] = self._extract_cgpa(text)
        
        return info
    
    def _extract_cgpa(self, text: str) -> Optional[float]:
        """Extract CGPA from text"""
        import re
        patterns = [
            r'CGPA[:\s]+(\d+\.?\d*)',
            r'CGPA[:\s]+(\d+\.?\d*)/10',
            r'overall[:\s]+(\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    def classify_document(self, filename: str, file_path: str) -> str:
        """Classify document type based on content"""
        if 'pdf' in filename.lower():
            text = self.extract_text_from_pdf(file_path)
            
            if 'mark' in text.lower() or 'grade' in text.lower():
                return 'marksheet'
            elif 'identity' in text.lower() or 'aadhar' in text.lower():
                return 'id_proof'
            elif 'income' in text.lower():
                return 'income_certificate'
        
        return 'other'