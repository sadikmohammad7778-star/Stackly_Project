from typing import List
from datetime import datetime

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.security.role_dependency import require_company_admin
from app.models.user import User

from app.schemas.import_schema import (
    ImportUploadResponse,
    ImportValidateRequest,
    ImportValidationResponse,
    ImportProcessRequest,
    ImportResultResponse,
    ImportHistoryResponse,
    ImportStatusResponse,
    ImportCancelResponse,
)

from app.services.background_job_service import create_job
from app.services import import_service


router = APIRouter(
    prefix="/imports",
    tags=["Imports"],
)


@router.post(
    "/upload",
    response_model=ImportUploadResponse,
)
def upload_import(
    import_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return import_service.upload_import(
        db=db,
        file=file,
        import_type=import_type,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.post(
    "/validate",
    response_model=ImportValidationResponse,
)
def validate_import(
    request: ImportValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return import_service.validate_import(
        db=db,
        import_id=request.import_id,
        company_id=current_user.company_id,
    )


@router.post(
    "/process",
    response_model=ImportResultResponse,
)
def process_import(
    request: ImportProcessRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    import_history = import_service.get_import(
        db=db,
        import_id=request.import_id,
        company_id=current_user.company_id,
    )

    if import_history.status == "Cancelled":
        raise HTTPException(
            status_code=400,
            detail="This import has been cancelled.",
        )

    if import_history.status not in {"Uploaded", "Validated"}:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Import cannot be processed from status "
                f"'{import_history.status}'."
            ),
        )

    job = create_job(
        db=db,
        job_type="import",
        company_id=current_user.company_id,
        triggered_by=current_user.id,
    )

    import_history.status = "Processing"
    import_history.started_at = datetime.utcnow()
    import_history.completed_at = None
    import_history.processed_records = 0
    import_history.successful_records = 0
    import_history.failed_records = 0
    import_history.progress_percentage = 0

    try:
        db.commit()
        db.refresh(import_history)
        db.refresh(job)
    except Exception:
        db.rollback()
        raise

    background_tasks.add_task(
        import_service.process_import_background,
        request.import_id,
        current_user.company_id,
        current_user.id,
        job.id,
    )

    return {
        "import_id": import_history.id,
        "status": "Processing",
        "total_records": import_history.total_records,
        "valid_records": import_history.valid_records,
        "successful_records": 0,
        "failed_records": 0,
        "duplicate_records": import_history.duplicate_records,
        "skipped_records": import_history.skipped_records,
        "processed_records": 0,
        "progress_percentage": 0,
        "validation_failures": 0,
    }


@router.get(
    "/history",
    response_model=List[ImportHistoryResponse],
)
def get_import_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return import_service.get_import_history(
        db=db,
        company_id=current_user.company_id,
    )


@router.get(
    "/{import_id}/status",
    response_model=ImportStatusResponse,
)
def get_import_status(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return import_service.get_import_status(
        db=db,
        import_id=import_id,
        company_id=current_user.company_id,
    )


@router.post(
    "/{import_id}/cancel",
    response_model=ImportCancelResponse,
)
def cancel_import(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return import_service.cancel_import(
        db=db,
        import_id=import_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/template/{import_type}")
def download_import_template(
    import_type: str,
):
    file_bytes, filename = import_service.download_import_template(
        import_type=import_type,
    )

    return StreamingResponse(
        iter([file_bytes]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.get("/{import_id}")
def get_import_details(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    return import_service.get_import_details(
        db=db,
        import_id=import_id,
        company_id=current_user.company_id,
    )


@router.get("/{import_id}/failed-records")
def download_failed_records(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    file_bytes, filename = import_service.download_failed_records(
        db=db,
        import_id=import_id,
        company_id=current_user.company_id,
    )

    return StreamingResponse(
        iter([file_bytes]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )