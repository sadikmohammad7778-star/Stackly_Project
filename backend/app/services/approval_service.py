from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.approval_request import ApprovalRequest
from app.models.approval_history import ApprovalHistory
from app.models.workflow_config import WorkflowConfiguration
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.customer import Customer
from app.models.import_history import ImportHistory
from app.models.user import User
from app.services.import_service import process_import
from app.services.audit_service import create_audit_log


def get_request_for_approval(
    db: Session,
    request_id: int,
    current_user: User,
):
    request = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.id == request_id,
            ApprovalRequest.company_id == current_user.company_id,
        )
        .first()
    )

    if not request:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found.",
        )

    return request


def add_workflow_audit_log(
    db: Session,
    request: ApprovalRequest,
    user_id: int,
    action: str,
    description: str,
):
    create_audit_log(
        db=db,
        company_id=request.company_id,
        user_id=user_id,
        module="Workflow",
        action=action,
        resource_type="ApprovalRequest",
        resource_id=str(request.id),
        description=description,
        status="SUCCESS",
    )


def validate_approver(
    db: Session,
    request: ApprovalRequest,
    current_user: User,
):
    if request.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="Only pending requests can be processed.",
        )

    if request.company_id != current_user.company_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another company's request.",
        )

    if request.assigned_approver_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to process this request.",
        )

    configuration = (
        db.query(WorkflowConfiguration)
        .filter(
            WorkflowConfiguration.company_id == current_user.company_id,
            WorkflowConfiguration.request_type == request.request_type,
            WorkflowConfiguration.is_active == True,
        )
        .first()
    )

    if not configuration:
        raise HTTPException(
            status_code=400,
            detail="Workflow configuration is not active.",
        )

    if (
        request.requested_by == current_user.id
        and not configuration.allow_self_approval
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot approve your own request.",
        )

    return configuration


def apply_stock_adjustment(
    db: Session,
    request: ApprovalRequest,
):
    if request.related_entity_id is None:
        raise HTTPException(
            status_code=400,
            detail="Inventory ID is required.",
        )

    inventory = (
        db.query(Inventory)
        .filter(
            Inventory.id == request.related_entity_id,
            Inventory.company_id == request.company_id,
        )
        .first()
    )

    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found.",
        )

    changes = request.requested_changes or {}

    if "requested_stock" not in changes:
        raise HTTPException(
            status_code=400,
            detail="Requested stock value is missing.",
        )

    requested_stock = changes["requested_stock"]

    if not isinstance(requested_stock, int):
        raise HTTPException(
            status_code=400,
            detail="Requested stock must be an integer.",
        )

    if requested_stock < 0:
        raise HTTPException(
            status_code=400,
            detail="Requested stock cannot be negative.",
        )

    if inventory.current_stock != changes.get("current_stock"):
        raise HTTPException(
            status_code=409,
            detail="Inventory has changed since the request was created.",
        )

    difference = requested_stock - inventory.current_stock

    inventory.current_stock = requested_stock
    inventory.available_stock += difference

    if inventory.available_stock < 0:
        inventory.available_stock = 0

    if inventory.current_stock == 0:
        inventory.stock_status = "Out of Stock"
    elif inventory.current_stock <= inventory.reorder_level:
        inventory.stock_status = "Low Stock"
    else:
        inventory.stock_status = "In Stock"

    return inventory


def apply_product_deactivation(
    db: Session,
    request: ApprovalRequest,
):
    if request.related_entity_id is None:
        raise HTTPException(
            status_code=400,
            detail="Product ID is required.",
        )

    product = (
        db.query(Product)
        .filter(
            Product.id == request.related_entity_id,
            Product.company_id == request.company_id,
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    if not product.is_active:
        raise HTTPException(
            status_code=400,
            detail="Product is already inactive.",
        )

    product.is_active = False

    return product


def apply_product_price_change(
    db: Session,
    request: ApprovalRequest,
):
    if request.related_entity_id is None:
        raise HTTPException(
            status_code=400,
            detail="Product ID is required.",
        )

    product = (
        db.query(Product)
        .filter(
            Product.id == request.related_entity_id,
            Product.company_id == request.company_id,
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found.",
        )

    changes = request.requested_changes or {}

    if "requested_price" not in changes:
        raise HTTPException(
            status_code=400,
            detail="Requested price is missing.",
        )

    requested_price = changes["requested_price"]

    if not isinstance(requested_price, (int, float)):
        raise HTTPException(
            status_code=400,
            detail="Requested price must be numeric.",
        )

    if requested_price <= 0:
        raise HTTPException(
            status_code=400,
            detail="Requested price must be greater than zero.",
        )

    if "current_price" in changes:
        if float(product.unit_price) != float(changes["current_price"]):
            raise HTTPException(
                status_code=409,
                detail="Product price has changed since the request was created.",
            )

    product.unit_price = requested_price

    return product


def apply_customer_information_change(
    db: Session,
    request: ApprovalRequest,
):
    if request.related_entity_id is None:
        raise HTTPException(
            status_code=400,
            detail="Customer ID is required.",
        )

    customer = (
        db.query(Customer)
        .filter(
            Customer.id == request.related_entity_id,
            Customer.company_id == request.company_id,
        )
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found.",
        )

    changes = request.requested_changes or {}

    allowed_fields = {
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "city",
        "state",
        "country",
        "postal_code",
        "segment",
        "status",
    }

    for field, value in changes.items():
        if field.startswith("current_"):
            continue

        if field not in allowed_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Field '{field}' cannot be changed through workflow.",
            )

        if not hasattr(customer, field):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid customer field: {field}",
            )

        setattr(customer, field, value)

    return customer


def apply_inventory_import(
    db: Session,
    request: ApprovalRequest,
    approver_user_id: int,
):
    if request.related_entity_id is None:
        raise HTTPException(
            status_code=400,
            detail="Import ID is required.",
        )

    import_history = (
        db.query(ImportHistory)
        .filter(
            ImportHistory.id == request.related_entity_id,
            ImportHistory.company_id == request.company_id,
        )
        .first()
    )

    if not import_history:
        raise HTTPException(
            status_code=404,
            detail="Import record not found.",
        )

    allowed_statuses = {
        "Uploaded",
        "Validated",
        "Pending Approval",
    }

    if import_history.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                f"This import cannot be approved because "
                f"its current status is '{import_history.status}'."
            ),
        )

    result = process_import(
        db=db,
        import_id=import_history.id,
        company_id=request.company_id,
        user_id=approver_user_id,
    )

    return result


def apply_approved_change(
    db: Session,
    request: ApprovalRequest,
    approver_id: int,
):
    if request.request_type == "stock_adjustment":
        return apply_stock_adjustment(
            db,
            request,
        )

    if request.request_type == "product_deactivation":
        return apply_product_deactivation(
            db,
            request,
        )

    if request.request_type == "product_price_change":
        return apply_product_price_change(
            db,
            request,
        )

    if request.request_type == "customer_information_change":
        return apply_customer_information_change(
            db,
            request,
        )

    if request.request_type == "inventory_import":
        return apply_inventory_import(
            db,
            request,
            approver_id,
        )

    raise HTTPException(
        status_code=400,
        detail="Unsupported workflow request type.",
    )


def approve_request(
    db: Session,
    request_id: int,
    current_user: User,
    comments=None,
):
    request = get_request_for_approval(
        db,
        request_id,
        current_user,
    )

    validate_approver(
        db,
        request,
        current_user,
    )

    try:
        apply_approved_change(
            db,
            request,
            current_user.id,
        )

        request.status = "approved"
        request.completed_at = datetime.now(timezone.utc)

        history = ApprovalHistory(
            approval_request_id=request.id,
            company_id=current_user.company_id,
            user_id=current_user.id,
            action="REQUEST_APPROVED",
            from_status="pending_approval",
            to_status="approved",
            comments=comments,
            action_metadata={
                "request_type": request.request_type,
                "related_entity_type": request.related_entity_type,
                "related_entity_id": request.related_entity_id,
            },
        )

        db.add(history)

        add_workflow_audit_log(
            db=db,
            request=request,
            user_id=current_user.id,
            action="REQUEST_APPROVED",
            description=f"Workflow request #{request.id} approved.",
        )

        db.commit()
        db.refresh(request)

        return request

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Approval processing failed.",
        )


def reject_approval_request(
    db: Session,
    request_id: int,
    current_user: User,
    comments: str,
):
    request = get_request_for_approval(
        db,
        request_id,
        current_user,
    )

    validate_approver(
        db,
        request,
        current_user,
    )

    if not comments or not comments.strip():
        raise HTTPException(
            status_code=400,
            detail="Rejection reason is required.",
        )

    try:
        request.status = "rejected"
        request.completed_at = datetime.now(timezone.utc)

        history = ApprovalHistory(
            approval_request_id=request.id,
            company_id=current_user.company_id,
            user_id=current_user.id,
            action="REQUEST_REJECTED",
            from_status="pending_approval",
            to_status="rejected",
            comments=comments.strip(),
            action_metadata={
                "request_type": request.request_type,
                "related_entity_type": request.related_entity_type,
                "related_entity_id": request.related_entity_id,
            },
        )

        db.add(history)

        add_workflow_audit_log(
            db=db,
            request=request,
            user_id=current_user.id,
            action="REQUEST_REJECTED",
            description=f"Workflow request #{request.id} rejected.",
        )

        db.commit()
        db.refresh(request)

        return request

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Request rejection failed.",
        )