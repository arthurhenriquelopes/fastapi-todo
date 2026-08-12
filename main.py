import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from supabase import create_client, Client

load_dotenv()

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for a to-do list.",
    version="1.0"
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/tasks_db")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

class UserCredentials(BaseModel):
    email: str
    password: str

@app.post("/auth/signup", summary="Sign Up", status_code=201)
async def signup(creds: UserCredentials):
    if not creds.email or not creds.password:
        return JSONResponse(status_code=400, content={"error": "Missing email or password"})
    try:
        response = supabase.auth.sign_up({"email": creds.email, "password": creds.password})
        return response.user.model_dump() if response.user else {}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/auth/login", summary="Log In")
async def login(creds: UserCredentials):
    if not creds.email or not creds.password:
        return JSONResponse(status_code=400, content={"error": "Missing email or password"})
    try:
        response = supabase.auth.sign_in_with_password({"email": creds.email, "password": creds.password})
        return response.session.model_dump() if response.session else {}
    except Exception as e:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})

from fastapi import Request

@app.get("/public/info", summary="Public Info")
async def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile", summary="Private Profile")
async def protected_profile_unverified(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"error": "Access token required"})
    return {"message": "You provided a token, but it's not verified yet."}
