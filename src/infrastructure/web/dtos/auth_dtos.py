from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterUserRequestDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, description="Senha com no mínimo 8 caracteres")

class UserResponseDTO(BaseModel):
    id: UUID
    email: str
    created_at: datetime

class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"