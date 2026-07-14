from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config.dependency import get_db
from app.models.user import User
from app.security.jwt_handler import verify_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    
    payload = verify_access_token(token)
    

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user = (
        db.query(User)
        .filter(User.id == payload["user_id"])
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return user