import os
import re
from typing import Dict, Optional

from PyPDF2 import PdfReader
from docx import Document as DocxDocument

from app.models.user import User


class DocumentProcessor:
    """Process and extract information from uploaded documents"""

    def __init__(self):
        self.upload_folder = "app/static/uploads"

    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
        return ext in ["pdf", "doc", "docx", "png", "jpg", "jpeg"]

    def extract_text_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF"""
        try:
            reader = PdfReader(filepath)

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            return text

        except Exception as e:
            print("PDF extraction error:", e)
            return ""

    def extract_text_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = DocxDocument(filepath)

            text = []

            for para in doc.paragraphs:
                text.append(para.text)

            return "\n".join(text)

        except Exception as e:
            print("DOCX extraction error:", e)
            return ""

    def get_document_text(self, filepath: str) -> str:
        """Read document based on extension"""

        filepath = filepath.lower()

        if filepath.endswith(".pdf"):
            return self.extract_text_from_pdf(filepath)

        elif filepath.endswith(".docx"):
            return self.extract_text_from_docx(filepath)

        return ""

    def extract_user_info(self, user: User) -> Dict:
        """
        Extract scholarship-relevant information
        from uploaded documents
        """

        info = {}

        for doc in user.documents:

            if not doc.file_path:
                continue

            text = self.get_document_text(doc.file_path)

            if not text:
                continue

            print("\n===== DOCUMENT TEXT =====")
            print(text[:1000])

            # Marksheet
            if doc.document_type == "marksheet":

                cgpa = self._extract_cgpa(text)

                if cgpa is not None:
                    info["cgpa_extracted"] = cgpa

            # Income Certificate
            elif doc.document_type == "income_certificate":

                income = self._extract_income(text)

                if income is not None:
                    info["income_extracted"] = income

            # Category Certificate
            elif doc.document_type == "category_certificate":

                category = self._extract_category(text)

                if category:
                    info["category_extracted"] = category

        return info

    def _extract_cgpa(self, text: str) -> Optional[float]:
        """Extract CGPA"""

        patterns = [
            r"CGPA[:\s]+(\d+\.?\d*)",
            r"Overall\s*CGPA[:\s]+(\d+\.?\d*)",
            r"Semester\s*CGPA[:\s]+(\d+\.?\d*)",
            r"(\d+\.\d+)\s*/\s*10"
        ]

        for pattern in patterns:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                try:
                    return float(match.group(1))
                except:
                    pass

        return None

    def _extract_income(self, text: str) -> Optional[int]:
        """Extract annual income"""

        patterns = [
            r"Income[:\s₹]*([\d,]+)",
            r"Annual Income[:\s₹]*([\d,]+)",
            r"Family Income[:\s₹]*([\d,]+)",
            r"Income Certificate[:\s₹]*([\d,]+)"
        ]

        for pattern in patterns:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                try:
                    value = match.group(1).replace(",", "")
                    return int(value)
                except:
                    pass

        return None

    def _extract_category(self, text: str) -> Optional[str]:
        """Extract caste category"""

        text = text.upper()

        if "SC" in text:
            return "SC"

        if "ST" in text:
            return "ST"

        if "OBC" in text:
            return "OBC"

        if "EWS" in text:
            return "EWS"

        return "GENERAL"

    def classify_document(self, filename: str, file_path: str) -> str:
        """
        Classify uploaded document
        """

        text = self.get_document_text(file_path)

        if not text:
            return "other"

        text = text.lower()

        if (
            "cgpa" in text
            or "marks memo" in text
            or "grade" in text
            or "semester" in text
        ):
            return "marksheet"

        if (
            "income certificate" in text
            or "annual income" in text
            or "family income" in text
        ):
            return "income_certificate"

        if (
            "aadhar" in text
            or "aadhaar" in text
            or "identity" in text
        ):
            return "id_proof"

        if (
            "caste certificate" in text
            or "community certificate" in text
            or "obc" in text
            or "sc" in text
            or "st" in text
        ):
            return "category_certificate"

        return "other"