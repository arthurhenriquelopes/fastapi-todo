# FlyRank Backend Engineering Internship

![FlyRank Internship](https://img.shields.io/badge/FlyRank-Backend%20AI%20Engineering-success)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)

## About
Welcome to my backend engineering portfolio for the **FlyRank Internship (Backend AI Engineering Track)**. This repository is a monorepo that houses a full-stack, AI-powered system designed to demonstrate professional engineering practices. It combines a robust Python/FastAPI backend with a React frontend, integrating modern tools like Supabase, Docker, PostgreSQL, OpenAI (OpenRouter), and Inngest.

Over the course of this internship, I have built multiple features scaling from a simple CRUD API up to complex, resilient AI background workflows.

---

## 📚 Assignments & Features

### 1. The Core: To-Do CRUD API & Dockerization (A1, A2, A3)
The foundation of the project is a blazing-fast CRUD API built with **FastAPI** and backed by a **PostgreSQL** database. 
- **Features:** Create, Read, Update, and Delete tasks. 
- **Persistence:** Fully containerized using `docker-compose.yml` to ensure deterministic setups.
- **Documentation:** Interactive Swagger UI generated automatically.

```json
// Example Response: GET /tasks
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Complete Backend Internship",
      "completed": false
    }
  ]
}
```
### 2. Security: Supabase JWT Authentication (BE-03)
To secure the application, I integrated **Supabase Auth**.
- **Features:** User Sign-up, Login, and Logout routes.
- **Protection:** Protected profile routes wrapped in a dependency that verifies the JWT token signature and decodes the user session.
- **Swagger Integration:** Configured the OpenAPI spec to natively accept Bearer Tokens for testing authenticated routes.

```python
# Protected Route Example
@router.get("/profile")
async def get_profile(user: User = Depends(verify_supabase_jwt)):
    return {"user_id": user.id, "email": user.email}
```
### 3. Data Collection: The Polite Scraper (A9)
A Python scraper built to cleanly extract e-commerce data from a practice sandbox.
- **Features:** Fetches catalogue pages, extracts nested book data, and caches responses to disk to prevent hammering the server.
- **Politeness:** Implements 0.5s delays, custom User-Agents, and respects failure limits.
- **Validation:** Uses Pydantic to strictly parse unstructured HTML prices ("£51.77") into valid Floats, quarantining bad data.

### 4. AI Integration: Triage LLM Endpoint (A17)
Integrating a Large Language Model the professional way—not as a chatbot, but as a rigid classification tool.
- **Features:** The `POST /triage` endpoint takes a messy customer support message and asks an LLM (via OpenRouter) to classify the category and urgency.
- **Resilience:** If the LLM returns invalid JSON or disobeys the schema, the system catches the exception and sends a **Repair Prompt** automatically.
- **Safety:** Built with strict timeouts, Cost Logging (tokens per request), and a deterministic Kill Switch (`LLM_ENABLED=false`).

### 5. Asynchronous Scale: Background Jobs (BE-06)
AI calls are slow. Professional APIs don't block the main thread waiting for an LLM to type.
- **Features:** Moved the Triage LLM call into a background worker using FastAPI `BackgroundTasks` and a SQL job queue.
- **Workflow:** The endpoint immediately returns `202 Accepted` and a `job_id`. Clients can poll `GET /triage/{job_id}` to retrieve the results.
- **Idempotency:** Implemented SHA-256 payload hashing so identical requests won't trigger duplicate LLM calls, saving API quota.

```python
@inngest.create_function(id="process-triage", name="Process Ticket Triage")
async def process_triage(ctx, step):
    job_id = ctx.event.data["job_id"]
    
    # AI Analysis in Background (No HTTP blocking)
    ai_result = await step.run("llm_analysis", analyze_ticket)
    
    # Secure Database Update
    await step.run("update_db", update_status)
    
    return {"status": "completed", "job_id": job_id}
```
### 6. Orchestration: AI Decision Flow with React Flow & Inngest (W7)
A complete Visual AI Workflow Editor where developers can design branching logic for LLMs.
- **Frontend (React Flow):** A Vite + Tailwind application (`frontend/`) where users can add nodes, write prompts, and draw YES/NO paths visually.
- **Backend Orchestration (Inngest):** The graph is sent to the FastAPI backend, where an **Inngest** function dynamically traverses the nodes. At each node, it sends the prompt to the AI, forcing a binary `YES/NO` answer, and routes the execution path accordingly.

```jsx
// React Flow Custom Node Example
const AiNode = ({ data }) => (
  <div className="bg-slate-900 border border-slate-700 text-white rounded p-4 shadow-xl">
    <Handle type="target" position={Position.Top} />
    <div className="font-mono text-sm text-electric-blue">AI Agent:</div>
    <div className="mt-2 text-xs">{data.prompt}</div>
    <Handle type="source" position={Position.Bottom} />
  </div>
);
```
---

## 🚀 How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/arthurhenriquelopes/fastapi-todo.git
   cd fastapi-todo
   ```

2. **Setup Environment:**
   Create a `.env` file in the root directory using `.env.example` as a template and provide your OpenRouter and Supabase keys.

3. **Start the Backend:**
   ```bash
   docker compose up --build -d
   ```
   The API will be live at `http://localhost:8000/docs`.

4. **Start the Visual Editor (Frontend):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
