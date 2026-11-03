import os
import uuid
import re
from fastapi import UploadFile

from app.core.config import settings
from app.core.errors import ValidationException


class StorageService:
    def __init__(self, base_dir: str = None):
        self.base_dir = os.path.abspath(base_dir or settings.STORAGE_LOCAL_DIR)
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        # Keep only alphanumeric, dots, underscores, dashes
        clean = re.sub(r"[^\w\.-]", "_", os.path.basename(filename))
        return clean or "document.pdf"

    def save_upload(self, user_id: str, file: UploadFile, max_size_bytes: int = 10 * 1024 * 1024) -> tuple[str, int]:
        # Validate MIME type
        if file.content_type != "application/pdf":
            raise ValidationException("Only PDF resumes are currently supported.", details=[{"field": "file", "mime": file.content_type}])

        clean_filename = self._sanitize_filename(file.filename or "resume.pdf")
        user_folder = os.path.join(self.base_dir, user_id)
        os.makedirs(user_folder, exist_ok=True)

        storage_key = f"{user_id}/{uuid.uuid4().hex}_{clean_filename}"
        destination_path = os.path.join(self.base_dir, storage_key)

        size = 0
        file.file.seek(0)
        first_bytes = file.file.read(4)
        if first_bytes != b"%PDF":
            raise ValidationException("Uploaded file is not a valid PDF document.")

        file.file.seek(0)
        with open(destination_path, "wb") as buffer:
            while chunk := file.file.read(1024 * 64):
                size += len(chunk)
                if size > max_size_bytes:
                    buffer.close()
                    if os.path.exists(destination_path):
                        os.remove(destination_path)
                    raise ValidationException(f"File size exceeds maximum allowed limit of {max_size_bytes // (1024 * 1024)}MB.")
                buffer.write(chunk)

        return storage_key, size

    def get_file_path(self, storage_key: str) -> str:
        safe_path = os.path.abspath(os.path.join(self.base_dir, storage_key))
        if not safe_path.startswith(self.base_dir):
            raise ValidationException("Invalid storage key path traversal attempt.")
        if not os.path.exists(safe_path):
            raise ValidationException("Referenced file does not exist in storage.")
        return safe_path

    def delete_file(self, storage_key: str) -> bool:
        try:
            path = self.get_file_path(storage_key)
            if os.path.exists(path):
                os.remove(path)
                return True
        except Exception:
            pass
        return False


storage_service = StorageService()

