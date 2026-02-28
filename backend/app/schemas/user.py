import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, SecretStr


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr
    full_name: str


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    sub: str        # user id as string
    token_type: str  # "access" or "refresh"
