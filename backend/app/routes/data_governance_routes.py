import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.models.approval_request import ApprovalRequest
from app.models.audit_log import AuditLog
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user import User
from app.security.auth_dependency import get_current_user
from app.security.permission_dependency import require_permission


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/data-governance",
    tags=["Data Governance"],
)


class RolePermissionUpdate(BaseModel):
    company_id: Optional[int] = None
    permission_ids: List[int] = Field(default_factory=list)


def ensure_company_access(current_user: User):
    if current_user.role != "Super Admin" and current_user.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not associated with a company.",
        )


def get_target_company_id(
    current_user: User,
    company_id: Optional[int],
) -> int:
    ensure_company_access(current_user)

    if current_user.role == "Super Admin":
        if company_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Super Admin must specify a company_id.",
            )
        return company_id

    if company_id is not None and company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access another company's permissions.",
        )

    return current_user.company_id


def ensure_company_exists(db: Session, company_id: int):
    from app.models.company import Company

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found.",
        )


def ensure_company_admin_access(
    current_user: User,
    company_id: int,
):
    if current_user.role != "Super Admin":
        if current_user.role != "Company Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Super Admin or Company Admin can manage permissions.",
            )

        if current_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot manage another company's permissions.",
            )


def write_audit_log(
    db: Session,
    current_user: User,
    company_id: int,
    action: str,
    description: str,
    resource_type: str,
    resource_id: Optional[int],
    before_values: dict,
    after_values: dict,
):
    db.add(
        AuditLog(
            company_id=company_id,
            user_id=current_user.id,
            module="Data Governance",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            before_values=before_values,
            after_values=after_values,
            status="SUCCESS",
        )
    )


@router.get("/reports")
def get_reports(
    current_user: User = Depends(
        require_permission("reports", "view")
    ),
):
    return {
        "message": "Authorized access",
        "user_id": current_user.id,
    }


@router.get("/dashboard")
def get_governance_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in {"Super Admin", "Company Admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view the Data Governance dashboard.",
        )

    ensure_company_access(current_user)

    if current_user.role == "Super Admin":
        user_query = db.query(User)
        request_query = db.query(ApprovalRequest)
        audit_query = db.query(AuditLog)
    else:
        user_query = db.query(User).filter(
            User.company_id == current_user.company_id
        )
        request_query = db.query(ApprovalRequest).filter(
            ApprovalRequest.company_id == current_user.company_id
        )
        audit_query = db.query(AuditLog).filter(
            AuditLog.company_id == current_user.company_id
        )

    total_users = user_query.count()
    active_users = user_query.filter(User.status.is_(True)).count()
    inactive_users = user_query.filter(User.status.is_(False)).count()

    total_roles = (
        user_query.with_entities(
            func.count(distinct(User.role))
        ).scalar()
        or 0
    )

    pending_requests = request_query.filter(
        func.lower(ApprovalRequest.status).in_(
            ["pending", "submitted"]
        )
    ).count()

    elevated_users = user_query.filter(
        User.role.in_(["Super Admin", "Company Admin"])
    ).count()

    recent_permission_changes = (
        audit_query.filter(
            AuditLog.module == "Data Governance",
            AuditLog.action.in_(
                [
                    "ROLE_PERMISSIONS_UPDATED",
                    "ROLE_PERMISSION_REVOKED",
                    "ACCESS_GRANTED",
                    "ACCESS_REVOKED",
                ]
            ),
        )
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )

    recent_changes = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "description": log.description,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "status": log.status,
            "created_at": (
                log.created_at.isoformat()
                if log.created_at
                else None
            ),
        }
        for log in recent_permission_changes
    ]

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "total_roles": total_roles,
        "pending_access_requests": pending_requests,
        "users_with_elevated_permissions": elevated_users,
        "recent_permission_changes": recent_changes,
        "last_access_review_date": None,
    }


@router.get("/roles")
def get_roles(
    company_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in {"Super Admin", "Company Admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view roles.",
        )

    target_company_id = get_target_company_id(
        current_user,
        company_id,
    )

    ensure_company_exists(db, target_company_id)

    query = db.query(
        User.role,
        func.count(User.id).label("user_count"),
    ).filter(
        User.company_id == target_company_id,
        User.role.isnot(None),
        User.role != "",
    )

    roles = query.group_by(User.role).order_by(User.role).all()

    return [
        {
            "role": role,
            "user_count": user_count,
        }
        for role, user_count in roles
    ]


@router.get("/permissions")
def get_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in {
        "Super Admin",
        "Company Admin",
        "Employee",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view permissions.",
        )

    permissions = (
        db.query(Permission)
        .filter(Permission.is_active.is_(True))
        .order_by(Permission.module, Permission.action)
        .all()
    )

    return [
        {
            "id": permission.id,
            "module": permission.module,
            "action": permission.action,
            "code": permission.code,
            "description": permission.description,
        }
        for permission in permissions
    ]


@router.get("/permission-matrix")
def get_permission_matrix(
    company_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in {"Super Admin", "Company Admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view the permission matrix.",
        )

    target_company_id = get_target_company_id(
        current_user,
        company_id,
    )

    ensure_company_exists(db, target_company_id)

    roles = sorted(
        {
            role
            for (role,) in (
                db.query(User.role)
                .filter(
                    User.company_id == target_company_id,
                    User.role.isnot(None),
                    User.role != "",
                )
                .distinct()
                .all()
            )
        }
    )

    permissions = (
        db.query(Permission)
        .filter(Permission.is_active.is_(True))
        .order_by(Permission.module, Permission.action)
        .all()
    )

    assignments = (
        db.query(RolePermission)
        .filter(
            RolePermission.company_id == target_company_id
        )
        .all()
    )

    assigned = {
        (item.role, item.permission_id)
        for item in assignments
    }

    return {
        "company_id": target_company_id,
        "roles": roles,
        "permissions": [
            {
                "id": permission.id,
                "module": permission.module,
                "action": permission.action,
                "code": permission.code,
            }
            for permission in permissions
        ],
        "matrix": [
            {
                "role": role,
                "permissions": [
                    permission.code
                    for permission in permissions
                    if (role, permission.id) in assigned
                ],
            }
            for role in roles
        ],
    }


@router.put("/roles/{role}/permissions")
def update_role_permissions(
    role: str,
    payload: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("data_governance", "manage_access")
    ),
):
    target_company_id = get_target_company_id(
        current_user,
        payload.company_id,
    )

    ensure_company_exists(db, target_company_id)
    ensure_company_admin_access(current_user, target_company_id)

    allowed_roles = {
        "Company Admin",
        "Employee",
        "Analyst",
        "Manager",
    }

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role.",
        )

    if len(payload.permission_ids) != len(set(payload.permission_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate permission IDs are not allowed.",
        )

    permissions = (
        db.query(Permission)
        .filter(
            Permission.id.in_(payload.permission_ids),
            Permission.is_active.is_(True),
        )
        .all()
        if payload.permission_ids
        else []
    )

    if len(permissions) != len(payload.permission_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more permission IDs are invalid or inactive.",
        )

    existing_query = db.query(RolePermission).filter(
        RolePermission.company_id == target_company_id,
        RolePermission.role == role,
    )

    existing = existing_query.all()
    before_permissions = sorted(
        item.permission_id for item in existing
    )
    new_permission_ids = sorted(payload.permission_ids)

    try:
        for item in existing:
            db.delete(item)

        db.flush()

        for permission_id in new_permission_ids:
            db.add(
                RolePermission(
                    company_id=target_company_id,
                    role=role,
                    permission_id=permission_id,
                )
            )

        write_audit_log(
            db=db,
            current_user=current_user,
            company_id=target_company_id,
            action="ROLE_PERMISSIONS_UPDATED",
            description=f"Permissions updated for role: {role}",
            resource_type="Role",
            resource_id=None,
            before_values={
                "permission_ids": before_permissions,
            },
            after_values={
                "permission_ids": new_permission_ids,
            },
        )

        db.commit()

        return {
            "message": "Role permissions updated successfully.",
            "company_id": target_company_id,
            "role": role,
            "permission_ids": new_permission_ids,
        }

    except Exception:
        db.rollback()
        logger.exception(
            "Failed to update permissions for role '%s' in company %s",
            role,
            target_company_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update role permissions.",
        )


@router.delete("/roles/{role}/permissions/{permission_id}")
def revoke_role_permission(
    role: str,
    permission_id: int,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("data_governance", "manage_access")
    ),
):
    target_company_id = get_target_company_id(
        current_user,
        company_id,
    )

    ensure_company_exists(db, target_company_id)
    ensure_company_admin_access(current_user, target_company_id)

    if role == "Super Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin permissions cannot be modified here.",
        )

    assignment = (
        db.query(RolePermission)
        .filter(
            RolePermission.company_id == target_company_id,
            RolePermission.role == role,
            RolePermission.permission_id == permission_id,
        )
        .first()
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role permission assignment not found.",
        )

    try:
        permission = (
            db.query(Permission)
            .filter(Permission.id == permission_id)
            .first()
        )

        write_audit_log(
            db=db,
            current_user=current_user,
            company_id=target_company_id,
            action="ROLE_PERMISSION_REVOKED",
            description=(
                f"Permission "
                f"{permission.code if permission else permission_id} "
                f"revoked from role: {role}"
            ),
            resource_type="Role",
            resource_id=None,
            before_values={
                "permission_id": permission_id,
            },
            after_values={
                "permission_id": None,
            },
        )

        db.delete(assignment)
        db.commit()

        return {
            "message": "Permission revoked successfully.",
            "company_id": target_company_id,
            "role": role,
            "permission_id": permission_id,
        }

    except Exception:
        db.rollback()
        logger.exception(
            "Failed to revoke permission %s from role '%s' in company %s",
            permission_id,
            role,
            target_company_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke role permission.",
        )