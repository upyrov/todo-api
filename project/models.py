from datetime import date
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class TaskStatus(str, Enum):
    DONE = "done"
    UNDONE = "undone"


class TaskBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.UNDONE)
    priority: int = Field(default=5, ge=1)
    category: Optional[str] = Field(default=None, index=True)
    due_date: Optional[date] = None


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    category: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    due_date: Optional[date] = None
