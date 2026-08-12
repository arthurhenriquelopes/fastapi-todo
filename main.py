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

class Task(TaskBase):
    id: int

tasks_db: List[dict] = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Read a book", "done": True},
    {"id": 3, "title": "Write some code", "done": False}
]

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
