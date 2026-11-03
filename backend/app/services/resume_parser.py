import os
from pypdf import PdfReader
from app.core.errors import ValidationException


def extract_text_from_pdf(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise ValidationException("PDF file not found for extraction.")

    try:
        reader = PdfReader(file_path)
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append(text.strip())

        full_text = "\n\n".join(extracted_pages).strip()
        if not full_text:
            raise ValidationException("The uploaded PDF does not contain extractable text (it might be a scanned image).")
        return full_text
    except Exception as e:
        if isinstance(e, ValidationException):
            raise e
        raise ValidationException(f"Failed to extract text from PDF document: {str(e)}")

