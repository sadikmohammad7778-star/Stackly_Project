from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    company_id: int
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    company_id: int
    name: str
    email: EmailStr
    role: str
    status: bool

    class Config:
        from_attributes = True

class RefreshTokenRequest(BaseModel):
    refresh_token: str
