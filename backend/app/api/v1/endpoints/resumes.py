from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user
from app.core.errors import NotFoundException
from app.models.user import User
from app.models.resume import Resume, ResumeAnalysis
from app.models.activity import UserActivity
from app.schemas.resume import ResumeResponse, ResumeAnalysisResponse
from app.services.storage import storage_service
from app.services.resume_service import resume_service

router = APIRouter()


@router.post(
    "/resumes",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new PDF resume",
)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    storage_key, file_size = storage_service.save_upload(user_id=current_user.id, file=file)

    resume = Resume(
        user_id=current_user.id,
        file_storage_key=storage_key,
        original_filename=file.filename or "resume.pdf",
        mime_type=file.content_type or "application/pdf",
        file_size=file_size,
        status="uploaded",
    )
    db.add(resume)
    db.flush()

    activity = UserActivity(
        user_id=current_user.id,
        activity_type="resume_uploaded",
        related_record_type="resume",
        related_record_id=resume.id,
        details={"filename": resume.original_filename, "size": file_size},
    )
    db.add(activity)
    db.commit()
    db.refresh(resume)

    return ResumeResponse.model_validate(resume)


@router.get(
    "/resumes",
    response_model=List[ResumeResponse],
    summary="List authenticated user's resumes",
)
def list_user_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(desc(Resume.created_at))
        .all()
    )
    results = []
    for r in resumes:
        latest_analysis = (
            db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.resume_id == r.id)
            .order_by(desc(ResumeAnalysis.created_at))
            .first()
        )
        res_data = ResumeResponse.model_validate(r)
        if latest_analysis:
            res_data.analysis = ResumeAnalysisResponse.model_validate(latest_analysis)
        results.append(res_data)
    return results


@router.get(
    "/resumes/{resume_id}",
    response_model=ResumeResponse,
    summary="Get resume details",
)
def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise NotFoundException("Resume not found or access denied.")

    latest_analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume.id)
        .order_by(desc(ResumeAnalysis.created_at))
        .first()
    )
    res_data = ResumeResponse.model_validate(resume)
    if latest_analysis:
        res_data.analysis = ResumeAnalysisResponse.model_validate(latest_analysis)
    return res_data


@router.delete(
    "/resumes/{resume_id}",
    summary="Delete a resume and its stored file",
)
def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise NotFoundException("Resume not found or access denied.")

    storage_service.delete_file(resume.file_storage_key)
    db.delete(resume)
    db.commit()
    return {"message": "Resume and associated analyses deleted successfully."}


@router.post(
    "/resumes/{resume_id}/analyze",
    response_model=ResumeAnalysisResponse,
    summary="Trigger AI analysis of uploaded resume",
)
def analyze_resume_endpoint(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = resume_service.analyze_resume_for_user(
        resume_id=resume_id,
        user_id=current_user.id,
        db=db,
    )
    return ResumeAnalysisResponse.model_validate(analysis)


@router.get(
    "/resumes/{resume_id}/analysis",
    response_model=ResumeAnalysisResponse,
    summary="Get analysis result for a resume",
)
def get_resume_analysis(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise NotFoundException("Resume not found or access denied.")

    analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume_id, ResumeAnalysis.user_id == current_user.id)
        .order_by(desc(ResumeAnalysis.created_at))
        .first()
    )
    if not analysis:
        raise NotFoundException("No analysis found for this resume. Please analyze it first.")

    return ResumeAnalysisResponse.model_validate(analysis)


@router.get(
    "/resume-analyses/{analysis_id}",
    response_model=ResumeAnalysisResponse,
    summary="Get resume analysis by ID",
)
def get_resume_analysis_by_id(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == analysis_id, ResumeAnalysis.user_id == current_user.id).first()
    if not analysis:
        raise NotFoundException("Resume analysis not found or access denied.")

    return ResumeAnalysisResponse.model_validate(analysis)

