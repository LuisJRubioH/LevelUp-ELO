"""
api/schemas/auth.py
===================
Pydantic schemas para autenticación y tokens JWT.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(default="student", pattern="^(student|teacher)$")
    education_level: str | None = Field(default=None, pattern="^(universidad|colegio|semillero)$")
    grade: str | None = Field(default=None, pattern="^([6-9]|10|11)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos
    user_id: int
    username: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfile(BaseModel):
    user_id: int
    username: str
    role: str
    approved: bool
    education_level: str | None
    grade: str | None
