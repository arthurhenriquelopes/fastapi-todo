from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for a to-do list.",
    version="1.0"
)

def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    cursor = conn.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        conn.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", [
            ("Buy groceries", 0),
            ("Read a book", 1),
            ("Write some code", 0)
        ])
    conn.commit()
    conn.close()

init_db()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1)
    done: bool = False

class TaskCreate(BaseModel):
    title: str
    done: Optional[bool] = False

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class Task(TaskBase):
    id: int

tasks_db: List[dict] = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Write some code", "done": False}
]

def get_next_id() -> int:
    if not tasks_db:
        return 1
    return max(task["id"] for task in tasks_db) + 1

@app.get("/", summary="Root Endpoint", description="Returns API metadata.")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check", description="Returns ok if the API is running.")
async def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List Tasks", description="Returns the complete list of tasks.", response_model=List[Task])
async def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", summary="Get Task", description="Returns a specific task by ID.", response_model=Task)
async def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", summary="Create Task", description="Creates a new task.", response_model=Task, status_code=201)
async def create_task(task_in: dict):
    title = task_in.get("title")
    if title is None or str(title).strip() == "":
        return JSONResponse(status_code=400, content={"error": "title is required and cannot be empty"})
    
    new_task = {
        "id": get_next_id(),
        "title": str(title).strip(),
        "done": bool(task_in.get("done", False))
    }
    tasks_db.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", summary="Update Task", description="Updates an existing task.", response_model=Task)
async def update_task(task_id: int, task_in: dict):
    if not task_in:
        return JSONResponse(status_code=400, content={"error": "Body cannot be empty"})
    for task in tasks_db:
        if task["id"] == task_id:
            title = task_in.get("title")
            if title is not None:
                if str(title).strip() == "":
                    return JSONResponse(status_code=400, content={"error": "title cannot be empty"})
                task["title"] = str(title).strip()
            if "done" in task_in:
                task["done"] = bool(task_in["done"])
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", summary="Delete Task", description="Deletes a task by ID.", status_code=204)
async def delete_task(task_id: int):
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            del tasks_db[i]
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
