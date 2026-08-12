# FastAPI To-Do List CRUD (Docker + PostgreSQL Version)

This is a small API that manages a to-do list: you can **create** tasks, **read** them, **update** them, and **delete** them.
The data is now stored in a real **PostgreSQL** database running inside a Docker container.

Built as part of the Backend Track - Week 3 Assignment (A3).

## Why Docker and PostgreSQL?
We moved from a local SQLite database to a full PostgreSQL database to simulate a production-grade environment. Using **Docker Compose**, we can launch both the API and the database at the same time with a single command. The Postgres data is persisted using Docker volumes, meaning our tasks will survive container restarts.

*Note: The routes and services were untouched during this swap, proving that the storage layer is just an implementation detail!*

## How to Install & Run

Ensure you have [Docker](https://docs.docker.com/get-docker/) and `docker-compose` installed.
Simply run the following command in the project directory:

```bash
docker compose up -d
```
The API will be available at `http://localhost:8000`.

## How Persistence was Proven
To verify that the volume works correctly:
1. Ran `docker compose up -d`.
2. Created a new task using a `POST /tasks` request.
3. Restarted the containers with `docker compose down` and `docker compose up -d`.
4. The task was still there when checking `GET /tasks`.

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

## Swagger UI Screenshot
![Swagger UI](docs/swagger_screenshot.png)
