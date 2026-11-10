from typing import List

from fastapi import APIRouter, Depends, Request, File, UploadFile, HTTPException, Body
from sqlalchemy.orm import Session

from app.config.dependency import (
    get_db,
    get_current_user,
    require_integration_admin,
)
from app.models.user import User

from app.schemas.integration_schema import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
    IntegrationTestResponse,
    IntegrationUploadResponse,
    IntegrationPreviewResponse,
    IntegrationMappingUpdate,
    IntegrationMappingResponse,
    IntegrationSyncRequest,
    IntegrationSyncResponse,
    IntegrationSyncHistoryResponse,
    IntegrationSyncDetailResponse,
    IntegrationSyncErrorListResponse,
    IntegrationScheduleCreate,
    IntegrationScheduleUpdate,
    IntegrationScheduleResponse,
)

from app.services import integration_service
from app.services import integration_history_service

from app.services.integration_sync_service import (
    synchronize_products,
    retry_failed_product_record,
)

from app.services import integration_schedule_service

from app.services.integration_connection_service import (
    test_postgresql_connection,
    test_rest_api_connection,
)

router = APIRouter(
    prefix="/integrations",
    tags=["Enterprise Integrations"],
)


@router.post("/", response_model=IntegrationResponse)
def create_integration(
    integration: IntegrationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return integration_service.create_integration(
        db,
        integration,
        current_user.id,
        current_user.company_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.get("/", response_model=List[IntegrationResponse])
def get_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return integration_service.get_all_integrations(
        db,
        current_user.company_id,
    )


@router.post(
    "/{integration_id}/test-connection",
    response_model=IntegrationTestResponse,
)
def test_integration_connection(
    integration_id: int,
    current_user: User = Depends(require_integration_admin),
    db: Session = Depends(get_db),
):
    integration = integration_service.get_integration_by_id(
        db,
        integration_id,
        current_user.company_id,
    )

    if integration.source_type == "postgresql":
        return test_postgresql_connection(
            db,
            integration_id,
            current_user.company_id,
        )

    if integration.source_type == "rest_api":
        return test_rest_api_connection(
            db,
            integration_id,
            current_user.company_id,
        )

    raise HTTPException(
        status_code=400,
        detail="Connection testing is not supported for this connector type.",
    )


@router.get("/{integration_id}", response_model=IntegrationResponse)
def get_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return integration_service.get_integration_by_id(
        db,
        integration_id,
        current_user.company_id,
    )


@router.put("/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: int,
    integration: IntegrationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return integration_service.update_integration(
        db,
        integration_id,
        integration,
        current_user.id,
        current_user.company_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.delete("/{integration_id}")
def delete_integration(
    integration_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return integration_service.delete_integration(
        db,
        integration_id,
        current_user.id,
        current_user.company_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.post(
    "/{integration_id}/upload",
    response_model=IntegrationUploadResponse,
)
def upload_integration_file(
    integration_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return integration_service.upload_integration_csv(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        upload=file,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.get(
    "/{integration_id}/preview",
    response_model=IntegrationPreviewResponse,
)
def preview_integration_file(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return integration_service.preview_integration_csv(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
    )


@router.put(
    "/{integration_id}/mappings",
    response_model=List[IntegrationMappingResponse],
)
def save_integration_mappings(
    integration_id: int,
    mapping_data: IntegrationMappingUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return integration_service.save_integration_mappings(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        mappings=mapping_data.mappings,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )


@router.get(
    "/{integration_id}/mappings",
    response_model=List[IntegrationMappingResponse],
)
def get_integration_mappings(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return integration_service.get_integration_mappings(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
    )


@router.post(
    "/{integration_id}/sync",
    response_model=IntegrationSyncResponse,
)
def synchronize_integration(
    integration_id: int,
    sync_request: IntegrationSyncRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return synchronize_products(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        trigger_type=sync_request.trigger_type,
    )


@router.get(
    "/{integration_id}/syncs",
    response_model=IntegrationSyncHistoryResponse,
)
def get_integration_sync_history(
    integration_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset cannot be negative.",
        )

    return integration_history_service.get_sync_history(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{integration_id}/syncs/{sync_id}",
    response_model=IntegrationSyncDetailResponse,
)
def get_integration_sync_details(
    integration_id: int,
    sync_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return integration_history_service.get_sync_details(
        db=db,
        integration_id=integration_id,
        sync_id=sync_id,
        company_id=current_user.company_id,
    )


@router.get(
    "/{integration_id}/syncs/{sync_id}/errors",
    response_model=IntegrationSyncErrorListResponse,
)
def get_integration_sync_errors(
    integration_id: int,
    sync_id: int,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset cannot be negative.",
        )

    return integration_history_service.get_sync_errors(
        db=db,
        integration_id=integration_id,
        sync_id=sync_id,
        company_id=current_user.company_id,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{integration_id}/syncs/{sync_id}/errors/{error_id}/retry",
)
def retry_integration_sync_error(
    integration_id: int,
    sync_id: int,
    error_id: int,
    request: Request,
    corrected_source_data: dict = Body(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return retry_failed_product_record(
        db=db,
        integration_id=integration_id,
        sync_id=sync_id,
        error_id=error_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        corrected_source_data=corrected_source_data,
    )

@router.post(
    "/{integration_id}/schedule",
    response_model=IntegrationScheduleResponse,
)
def create_integration_schedule(
    integration_id: int,
    schedule_data: IntegrationScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return integration_schedule_service.create_integration_schedule(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
        schedule_data=schedule_data,
    )


@router.get(
    "/{integration_id}/schedule",
    response_model=IntegrationScheduleResponse,
)
def get_integration_schedule(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return integration_schedule_service.get_integration_schedule(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
    )


@router.put(
    "/{integration_id}/schedule",
    response_model=IntegrationScheduleResponse,
)
def update_integration_schedule(
    integration_id: int,
    schedule_data: IntegrationScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return integration_schedule_service.update_integration_schedule(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
        schedule_data=schedule_data,
    )


@router.delete(
    "/{integration_id}/schedule",
)
def delete_integration_schedule(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_integration_admin),
):
    return integration_schedule_service.delete_integration_schedule(
        db=db,
        integration_id=integration_id,
        company_id=current_user.company_id,
    )