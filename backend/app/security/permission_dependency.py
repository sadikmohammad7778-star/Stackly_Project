from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.models.user import User
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.security.auth_dependency import get_current_user


def require_permission(module: str, action: str):
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if current_user.role == "Super Admin":
            return current_user

        if current_user.company_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is not associated with a company.",
            )

        permission_code = f"{module}.{action}"

        permission = (
            db.query(Permission)
            .filter(
                Permission.code == permission_code,
                Permission.is_active.is_(True),
            )
            .first()
        )

        if permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission is not configured.",
            )

        role_permission = (
            db.query(RolePermission)
            .filter(
                RolePermission.company_id == current_user.company_id,
                RolePermission.role == current_user.role,
                RolePermission.permission_id == permission.id,
            )
            .first()
        )

        if role_permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return permission_checker