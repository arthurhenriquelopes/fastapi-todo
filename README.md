# FastAPI To-Do List CRUD

This is a small API that manages a to-do list: you can **create** tasks, **read** them, **update** them, and **delete** them — the four CRUD operations.
The data lives only in memory (no database yet).

Built as part of the Backend Track - Week 2 Assignment.

## How to Install & Run

Ensure you have Python 3.10+ installed. Then run the following command in the project directory:

```bash
pip install -r requirements.txt && uvicorn main:app --reload --port 8000
```

## Endpoints

| HTTP Method | Endpoint | Description |
| ----------- | -------- | ----------- |
| GET         | `/` | Root endpoint, describes the API |
| GET         | `/health` | Health check to see if server is alive |
| GET         | `/tasks` | Lists all tasks |
| GET         | `/tasks/{id}` | Gets a specific task by ID |
| POST        | `/tasks` | Creates a new task (requires JSON body with `title`) |
| PUT         | `/tasks/{id}` | Updates an existing task's `title` or `done` status |
| DELETE      | `/tasks/{id}` | Removes a task by ID |
