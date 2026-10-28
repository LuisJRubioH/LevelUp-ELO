"""
api/schemas/auth.py
===================
Pydantic schemas para autenticación y tokens JWT.
"""

from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    # Username or email: as long as the longest email registration accepts (254).
    username: str = Field(..., min_length=1, max_length=254)
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
    # Spec 004 FR-020 (N11): required of students, checked by the name filter in the endpoint.
    display_name: str | None = Field(default=None, max_length=200)

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
    # Spec 004 FR-030: a temporary password must be changed before anything else.
    must_change_password: bool = False
    # Spec 004 FR-020: the account's own display name (None on existing accounts).
    display_name: str | None = None


class PasswordChangeRequest(BaseModel):
    """Spec 004 FR-026. No length rule here: a 422 would echo the password back in its body."""

    current_password: str
    new_password: str


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
    must_change_password: bool = False
    display_name: str | None = None
    # Spec 009 FR-013: the account's own linked identification — only here and to the admin;
    # FR-014: an imported account's name is changed by the admin only.
    identification: str | None = None
    display_name_locked: bool = False


class DisplayNameRequest(BaseModel):
    """Spec 004 FR-025: a new display name, checked by the name filter (FR-020)."""

    display_name: str = Field(..., max_length=200)
