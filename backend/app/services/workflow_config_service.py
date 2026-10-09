from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.workflow_config import WorkflowConfiguration
from app.models.user import User

VALID_REQUEST_TYPES = {
    "stock_adjustment",
    "product_deactivation",
    "product_price_change",
    "customer_information_change",
    "inventory_import",
}


def create_workflow_configuration(
    db: Session,
    config_data,
    current_user: User,
):
    if current_user.role not in {"Super Admin", "Company Admin"}:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to manage workflow configurations.",
        )

    if config_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot manage another company's workflow configuration.",
        )

    if config_data.request_type not in VALID_REQUEST_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid request type.",
        )

    existing = (
        db.query(WorkflowConfiguration)
        .filter(
            WorkflowConfiguration.company_id == current_user.company_id,
            WorkflowConfiguration.request_type == config_data.request_type,
            WorkflowConfiguration.is_active == True,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="An active workflow configuration already exists for this request type.",
        )

    configuration = WorkflowConfiguration(
        company_id=current_user.company_id,
        request_type=config_data.request_type,
        approver_role=config_data.approver_role,
        approval_required=config_data.approval_required,
        allow_self_approval=config_data.allow_self_approval,
        is_active=config_data.is_active,
        created_by=current_user.id,
    )

    db.add(configuration)
    db.commit()
    db.refresh(configuration)

    return configuration


def get_workflow_configurations(
    db: Session,
    current_user: User,
):
    if current_user.role not in {"Super Admin", "Company Admin"}:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view workflow configurations.",
        )

    return (
        db.query(WorkflowConfiguration)
        .filter(
            WorkflowConfiguration.company_id == current_user.company_id
        )
        .order_by(WorkflowConfiguration.created_at.desc())
        .all()
    )


def get_workflow_configuration(
    db: Session,
    config_id: int,
    current_user: User,
):
    if current_user.role not in {"Super Admin", "Company Admin"}:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view workflow configurations.",
        )

    configuration = (
        db.query(WorkflowConfiguration)
        .filter(
            WorkflowConfiguration.id == config_id,
            WorkflowConfiguration.company_id == current_user.company_id,
        )
        .first()
    )

    if not configuration:
        raise HTTPException(
            status_code=404,
            detail="Workflow configuration not found.",
        )

    return configuration


def update_workflow_configuration(
    db: Session,
    config_id: int,
    config_data,
    current_user: User,
):
    configuration = get_workflow_configuration(
        db=db,
        config_id=config_id,
        current_user=current_user,
    )

    if config_data.approver_role is not None:
        configuration.approver_role = config_data.approver_role

    if config_data.approval_required is not None:
        configuration.approval_required = config_data.approval_required

    if config_data.allow_self_approval is not None:
        configuration.allow_self_approval = config_data.allow_self_approval

    if config_data.is_active is not None:
        if config_data.is_active:
            existing = (
                db.query(WorkflowConfiguration)
                .filter(
                    WorkflowConfiguration.company_id == current_user.company_id,
                    WorkflowConfiguration.request_type == configuration.request_type,
                    WorkflowConfiguration.is_active == True,
                    WorkflowConfiguration.id != configuration.id,
                )
                .first()
            )

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Another active workflow configuration already exists for this request type.",
                )

        configuration.is_active = config_data.is_active

    db.commit()
    db.refresh(configuration)

    return configuration