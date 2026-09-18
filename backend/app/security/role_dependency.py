from fastapi import Depends, HTTPException

from app.models.user import User
from app.security.auth_dependency import get_current_user


def require_super_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "Super Admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    return current_user


def require_company_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "Company Admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    return current_user


def require_employee(
    current_user: User = Depends(get_current_user),
):
    return current_user