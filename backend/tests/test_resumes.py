import io
import os
from pypdf import PdfWriter
from fastapi import UploadFile

from app.models.user import User
from app.models.resume import Resume
from app.models.skill import EvidenceRecord, UserCapability
from app.core.security import get_password_hash
from app.services.storage import storage_service
from app.services.resume_service import resume_service
from app.api.v1.endpoints.resumes import upload_resume, delete_resume


def _create_sample_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # Note: blank page is valid PDF with %PDF header
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


def test_resume_upload_and_storage(db_session, tmp_path):
    user = User(email="resume_test_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    pdf_bytes = _create_sample_pdf_bytes()
    upload = UploadFile(
        file=io.BytesIO(pdf_bytes),
        size=len(pdf_bytes),
        filename="John_Doe_Resume.pdf",
        headers={"content-type": "application/pdf"},
    )

    resume_dto = upload_resume(file=upload, current_user=user, db=db_session)
    assert resume_dto.original_filename == "John_Doe_Resume.pdf"
    assert resume_dto.mime_type == "application/pdf"
    assert resume_dto.status == "uploaded"

    # Verify physical file existence in storage
    resume_db = db_session.query(Resume).filter_by(id=resume_dto.id).first()
    assert resume_db is not None
    stored_path = storage_service.get_file_path(resume_db.file_storage_key)
    assert os.path.exists(stored_path)


def test_resume_ai_analysis_and_skill_ingestion(db_session, monkeypatch):
    user = User(email="ai_resume_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Mock extract_text_from_pdf to simulate rich extracted resume text
    mock_resume_text = """
    John Doe — Full Stack Engineer
    Education: B.Tech Computer Science, University of Technology (2020-2024)
    Experience: Software Engineering Intern at Tech Corp (6 months)
    Projects: Distributed Cache in Python and Redis; React Dashboard with FastAPI
    Technical Skills: Python, FastAPI, React, PostgreSQL, Docker, Data Structures
    """
    monkeypatch.setattr("app.services.resume_service.extract_text_from_pdf", lambda path: mock_resume_text)

    pdf_bytes = _create_sample_pdf_bytes()
    upload = UploadFile(
        file=io.BytesIO(pdf_bytes),
        size=len(pdf_bytes),
        filename="John_Doe_Rich.pdf",
        headers={"content-type": "application/pdf"},
    )
    resume_dto = upload_resume(file=upload, current_user=user, db=db_session)

    # Run analysis
    analysis = resume_service.analyze_resume_for_user(resume_id=resume_dto.id, user_id=user.id, db=db_session)

    assert analysis.status == "completed"
    assert len(analysis.strengths) > 0
    assert len(analysis.suggestions) > 0

    # Verify skills ingested as claimed evidence
    evidence = db_session.query(EvidenceRecord).filter_by(user_id=user.id, source_type="resume").all()
    assert len(evidence) >= 3  # Python, FastAPI, React, etc.

    # Verify user capabilities created with band='claimed' and confidence=0.5
    capabilities = db_session.query(UserCapability).filter_by(user_id=user.id).all()
    assert len(capabilities) >= 3
    assert all(c.estimated_band == "claimed" for c in capabilities)
    assert all(c.confidence == 0.5 for c in capabilities)


def test_resume_deletion(db_session):
    user = User(email="del_resume_user@example.com", password_hash=get_password_hash("pwd"), account_status="active")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    pdf_bytes = _create_sample_pdf_bytes()
    upload = UploadFile(
        file=io.BytesIO(pdf_bytes),
        size=len(pdf_bytes),
        filename="To_Delete.pdf",
        headers={"content-type": "application/pdf"},
    )
    resume_dto = upload_resume(file=upload, current_user=user, db=db_session)

    # Delete resume
    del_res = delete_resume(resume_id=resume_dto.id, current_user=user, db=db_session)
    assert "deleted successfully" in del_res["message"]

    # Verify deleted from DB
    assert db_session.query(Resume).filter_by(id=resume_dto.id).first() is None
