from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config.dependency import get_db, get_current_user
from app.models.background_job import BackgroundJob
from app.models.user import User
from app.schemas.background_job_schema import BackgroundJobResponse

router = APIRouter(
    prefix="/background-jobs",
    tags=["Background Jobs"],
)


@router.get("/", response_model=list[BackgroundJobResponse])
def list_background_jobs(
    status: str = None,
    job_type: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(BackgroundJob).filter(
        BackgroundJob.company_id == current_user.company_id
    )

    if status:
        query = query.filter(BackgroundJob.status == status)

    if job_type:
        query = query.filter(BackgroundJob.job_type == job_type)

    return (
        query.order_by(BackgroundJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )


@router.get("/{job_id}", response_model=BackgroundJobResponse)
def get_background_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = (
        db.query(BackgroundJob)
        .filter(
            BackgroundJob.id == job_id,
            BackgroundJob.company_id == current_user.company_id,
        )
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Background job not found",
        )

    return job