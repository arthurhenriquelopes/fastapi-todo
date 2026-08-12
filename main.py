from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

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

@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", response_model=Task, status_code=201)
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

@app.put("/tasks/{task_id}", response_model=Task)
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

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            del tasks_db[i]
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
