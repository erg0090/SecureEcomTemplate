import uuid
from datetime import UTC, datetime
from enum import Enum

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


class GradeLetter(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"
    W = "W"
    I = "I"


class Term(SQLModel, table=True):
    __tablename__ = "terms"
    __table_args__ = (Index("idx_term_chronology", "academic_year", "semester_name"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    semester_name: str
    academic_year: int


class Course(SQLModel, table=True):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("course_code", "term_id", name="uq_course_per_term"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    course_code: str
    title: str
    term_id: uuid.UUID = Field(foreign_key="terms.id", nullable=False, ondelete="CASCADE")
    professor_id: uuid.UUID = Field(foreign_key="professors.id", nullable=True, ondelete="Set Null")
    grade: GradeLetter | None = Field(
        default=None,
        sa_column=Column(SAEnum(GradeLetter, name="grade_letter_enum"), nullable=True),
    )
    total_allocated_weight: float = Field(default=0.0, nullable=False)


class CourseTask(SQLModel, table=True):
    __tablename__ = "course_tasks"
    __table_args__ = (
        UniqueConstraint("course_id", "task_title", name="uq_task_per_course"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_title: str
    weight: float
    course_id: uuid.UUID = Field(foreign_key="courses.id", nullable=False, ondelete="CASCADE")

class Professor(SQLModel, table=True):
    __tablename__ = "professors"
    __table_args__ = (
		UniqueConstraint("professor_name", name="uq_professor_name"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    professor_name: str
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
