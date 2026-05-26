from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from pydantic.fields import Undefined

# --- User schemas ---


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Task schemas ---


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: int = Field(default=Undefined, ge=1, le=5)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    completed: bool | None = None
    priority: int | None = Field(default=None, ge=1, le=5)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    priority: int
    created_at: datetime
    updated_at: datetime | None
    owner_id: int

    model_config = {"from_attributes": True}


# --- Pagination ---


class PaginatedResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    per_page: int
