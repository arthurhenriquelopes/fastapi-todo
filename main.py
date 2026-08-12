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

@app.get("/", summary="Root Endpoint", description="Returns API metadata.")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check", description="Returns ok if the API is running.")
async def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List Tasks", description="Returns the complete list of tasks.", response_model=List[Task])
async def get_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [{"id": t["id"], "title": t["title"], "done": bool(t["done"])} for t in tasks]

@app.get("/tasks/{task_id}", summary="Get Task", description="Returns a specific task by ID.", response_model=Task)
async def get_task(task_id: int):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"id": task["id"], "title": task["title"], "done": bool(task["done"])}

@app.post("/tasks", summary="Create Task", description="Creates a new task.", response_model=Task, status_code=201)
async def create_task(task_in: dict):
    title = task_in.get("title")
    if title is None or str(title).strip() == "":
        return JSONResponse(status_code=400, content={"error": "title is required and cannot be empty"})
    
    done = bool(task_in.get("done", False))
    conn = get_db()
    cursor = conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (str(title).strip(), done))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    return {"id": task_id, "title": str(title).strip(), "done": done}

@app.put("/tasks/{task_id}", summary="Update Task", description="Updates an existing task.", response_model=Task)
async def update_task(task_id: int, task_in: dict):
    if not task_in:
        return JSONResponse(status_code=400, content={"error": "Body cannot be empty"})
    
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    
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
        
    conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, done, task_id))
    conn.commit()
    conn.close()
    
    return {"id": task_id, "title": title, "done": bool(done)}

@app.delete("/tasks/{task_id}", summary="Delete Task", description="Deletes a task by ID.", status_code=204)
async def delete_task(task_id: int):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return
