from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.security.auth_dependency import get_current_user

from app.models.user import User

from app.schemas.import_schema import (
    ImportUploadResponse,
    ImportValidateRequest,
    ImportValidationResponse,
    ImportProcessRequest,
    ImportResultResponse,
    ImportHistoryResponse,
)

from app.services import import_service


# ============================================================
# Import Router
# ============================================================

router = APIRouter(
    prefix="/imports",
    tags=["Imports"],
)


# ============================================================
# Upload Import File
# ============================================================

@router.post(
    "/upload",
    response_model=ImportUploadResponse,
)
def upload_import(
    import_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return import_service.upload_import(
        db=db,
        file=file,
        import_type=import_type,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


# ============================================================
# Validate Import
# ============================================================

@router.post(
    "/validate",
    response_model=ImportValidationResponse,
)
def validate_import(
    request: ImportValidateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return import_service.validate_import(
        db=db,
        import_id=request.import_id,
        company_id=current_user.company_id,
    )


# ============================================================
# Process Import
# ============================================================

@router.post(
    "/process",
    response_model=ImportResultResponse,
)
def process_import(
    request: ImportProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return import_service.process_import(
        db=db,
        import_id=request.import_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


# ============================================================
# Import History
# ============================================================

@router.get(
    "/history",
    response_model=List[ImportHistoryResponse],
)
def get_import_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return import_service.get_import_history(
        db=db,
        company_id=current_user.company_id,
    )


# ============================================================
# Import Details
# ============================================================

@router.get(
    "/{import_id}",
)
def get_import_details(
    import_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return import_service.get_import_details(
        db=db,
        import_id=import_id,
        company_id=current_user.company_id,
    )
