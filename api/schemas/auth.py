"""
api/schemas/auth.py
===================
Pydantic schemas para autenticación y tokens JWT.
"""

from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(default="student", pattern="^(student|teacher)$")
    education_level: str | None = Field(
        default=None, pattern="^(universidad|colegio|semillero|concursos)$"
    )
    grade: str | None = Field(default=None, pattern="^([6-9]|10|11)$")
    email: str | None = Field(default=None, max_length=254)

    @model_validator(mode="after")
    def _semillero_needs_a_grade(self):
        """Spec 001 FR-028m: semillero has no catalogue without a grade from 6 to 11."""
        if self.education_level == "semillero" and self.grade is None:
            raise ValueError("Semillero requiere un grado de 6.º a 11.º.")
        return self


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
    email: str | None = None
