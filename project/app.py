from contextlib import asynccontextmanager
from datetime import date
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import Annotated, Optional

from .database import create_db_and_tables, engine
from .models import Task, TaskCreate, TaskStatus, TaskUpdate


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI(title="TODO API", version="1.0.0", lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://xrov-todo.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tasks", response_model=list[Task])
def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    overdue: Optional[bool] = Query(None, description="Filter overdue tasks"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: Optional[str] = Query(
        "priority", description="Sort by field (priority, id, title)"
    ),
    order: Optional[str] = Query("asc", description="Sort order (asc, desc)"),
):
    """
    Display a list of all tasks with optional filtering, searching, and sorting.

    - **status**: Filter by done/undone
    - **category**: Filter by category
    - **overdue**: Filter overdue tasks
    - **search**: Search text in title and description
    - **sort_by**: Sort by priority, id, or title (default: priority)
    - **order**: asc or desc (default: asc)
    """
    with Session(engine) as session:
        statement = select(Task)

        if status:
            statement = statement.where(Task.status == status)

        if category:
            statement = statement.where(Task.category == category)
        
        if overdue is not None:
            today = date.today()
            if overdue:
                statement = statement.where(
                    (Task.due_date < today) & (Task.status == TaskStatus.UNDONE)
                )
            else:
                statement = statement.where(
                    (Task.due_date >= today) | (Task.due_date.is_(None))
                )

        # Search in title and description (ILIKE for case-insensitive search)
        if search:
            search_term = f"%{search}%"
            statement = statement.where(
                (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
            )

        if sort_by == "priority":
            statement = statement.order_by(
                Task.priority.desc() if order.lower() == "desc" else Task.priority.asc()
            )
        elif sort_by == "title":
            statement = statement.order_by(
                Task.title.desc() if order.lower() == "desc" else Task.title.asc()
            )
        elif sort_by == "id":
            statement = statement.order_by(
                Task.id.desc() if order.lower() == "desc" else Task.id.asc()
            )

        tasks = session.exec(statement).all()
        return tasks


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    with Session(engine) as session:
        db_task = Task.model_validate(task)
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        session.delete(task)
        session.commit()


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task_data = task_update.model_dump(exclude_unset=True)
        for key, value in task_data.items():
            setattr(task, key, value)

        session.add(task)
        session.commit()
        session.refresh(task)
        return task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task


@app.get("/categories", response_model=list[str])
def get_categories():
    """Get all unique categories"""
    with Session(engine) as session:
        statement = select(Task.category).where(Task.category.is_not(None)).distinct()
        categories = session.exec(statement).all()
        return sorted([category for category in categories if category])


@app.get("/")
def root():
    return {"status": "ok", "message": "TODO API is running"}


def main():
    create_db_and_tables()


if __name__ == "__main__":
    main()
