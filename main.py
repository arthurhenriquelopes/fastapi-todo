import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv()

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for a to-do list.",
    version="1.0"
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/tasks_db")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

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

@app.get("/", summary="Root Endpoint")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check")
async def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List Tasks", response_model=List[Task])
async def get_tasks():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
    tasks = cursor.fetchall()
    conn.close()
    return [{"id": t["id"], "title": t["title"], "done": bool(t["done"])} for t in tasks]

@app.get("/tasks/{task_id}", summary="Get Task", response_model=Task)
async def get_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"id": task["id"], "title": task["title"], "done": bool(task["done"])}

@app.post("/tasks", summary="Create Task", response_model=Task, status_code=201)
async def create_task(task_in: dict):
    title = task_in.get("title")
    if title is None or str(title).strip() == "":
        return JSONResponse(status_code=400, content={"error": "title is required and cannot be empty"})
    
    done = bool(task_in.get("done", False))
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        (str(title).strip(), done)
    )
    task_id = cursor.fetchone()["id"]
    conn.commit()
    conn.close()
    
    return {"id": task_id, "title": str(title).strip(), "done": done}

@app.put("/tasks/{task_id}", summary="Update Task", response_model=Task)
async def update_task(task_id: int, task_in: dict):
    if not task_in:
        return JSONResponse(status_code=400, content={"error": "Body cannot be empty"})
    
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    title = task["title"]
    done = task["done"]
    
    if "title" in task_in:
        if task_in["title"] is None or str(task_in["title"]).strip() == "":
            conn.close()
            return JSONResponse(status_code=400, content={"error": "title cannot be empty"})
        title = str(task_in["title"]).strip()
        
    if "done" in task_in:
        done = bool(task_in["done"])
        
    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (title, done, task_id)
    )
    conn.commit()
    conn.close()
    
    return {"id": task_id, "title": title, "done": bool(done)}

@app.delete("/tasks/{task_id}", summary="Delete Task", status_code=204)
async def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return
