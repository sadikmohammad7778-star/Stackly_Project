from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.integration import Integration
from app.models.integration_sync import IntegrationSync
from app.models.integration_sync_error import IntegrationSyncError


def get_sync_history(
    db: Session,
    integration_id: int,
    company_id: int,
    limit: int = 20,
    offset: int = 0,
):
    integration = (
        db.query(Integration)
        .filter(
            Integration.id == integration_id,
            Integration.company_id == company_id,
        )
        .first()
    )

    if not integration:
        raise HTTPException(
            status_code=404,
            detail="Integration not found.",
        )

    query = (
        db.query(IntegrationSync)
        .filter(
            IntegrationSync.integration_id == integration_id,
            IntegrationSync.company_id == company_id,
        )
    )

    total = query.count()

    items = (
        query
        .order_by(IntegrationSync.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }


def get_sync_details(
    db: Session,
    integration_id: int,
    sync_id: int,
    company_id: int,
):
    sync = (
        db.query(IntegrationSync)
        .filter(
            IntegrationSync.id == sync_id,
            IntegrationSync.integration_id == integration_id,
            IntegrationSync.company_id == company_id,
        )
        .first()
    )

    if not sync:
        raise HTTPException(
            status_code=404,
            detail="Synchronization record not found.",
        )

    return sync


def get_sync_errors(
    db: Session,
    integration_id: int,
    sync_id: int,
    company_id: int,
    limit: int = 20,
    offset: int = 0,
):
    get_sync_details(
        db=db,
        integration_id=integration_id,
        sync_id=sync_id,
        company_id=company_id,
    )

    query = (
        db.query(IntegrationSyncError)
        .join(
            IntegrationSync,
            IntegrationSyncError.sync_id == IntegrationSync.id,
        )
        .filter(
            IntegrationSync.id == sync_id,
            IntegrationSync.integration_id == integration_id,
            IntegrationSync.company_id == company_id,
        )
    )

    total = query.count()

    items = (
        query
        .order_by(IntegrationSyncError.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }