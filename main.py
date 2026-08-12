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

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Access token required")
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        return user_response.user.model_dump() if user_response.user else {}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/protected/profile", summary="Private Profile")
async def protected_profile(user = Depends(verify_token)):
    return user

@app.post("/auth/logout", summary="Log Out", status_code=204)
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Access token required")
    token = credentials.credentials
    try:
        supabase.auth.sign_out(token)
    except:
        pass
    return


# --- Background Job / LLM Endpoint ---
from src.llm.schema import TriageInput, TriageOutput, CategoryEnum, UrgencyEnum, JobStatusEnum, TriageJobResponse
from fastapi import BackgroundTasks
import uuid
import hashlib

from fastapi.staticfiles import StaticFiles
import os
os.makedirs("static/reports", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS triage_jobs (
            id VARCHAR(36) PRIMARY KEY,
            idempotency_key VARCHAR(255) UNIQUE,
            status VARCHAR(20) NOT NULL,
            category VARCHAR(50),
            urgency VARCHAR(50),
            confidence FLOAT,
            reason TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS report_jobs (
            id VARCHAR(36) PRIMARY KEY,
            status VARCHAR(20) NOT NULL,
            download_url TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def process_triage_job(job_id: str, payload_text: str):
    import json
    import time
    from pydantic import ValidationError
    from src.llm.client import llm_client
    
    # Mark as processing
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE triage_jobs SET status = 'processing' WHERE id = %s", (job_id,))
    conn.commit()
    
    def mark_failed(error_msg: str):
        cursor.execute("UPDATE triage_jobs SET status = 'failed', error = %s WHERE id = %s", (error_msg, job_id))
        conn.commit()
        conn.close()
        
    def mark_completed(data: TriageOutput):
        cursor.execute('''
            UPDATE triage_jobs 
            SET status = 'completed', category = %s, urgency = %s, confidence = %s, reason = %s
            WHERE id = %s
        ''', (data.category.value, data.urgency.value, data.confidence, data.reason, job_id))
        conn.commit()
        conn.close()
    
    if os.environ.get("LLM_STUB") == "1":
        time.sleep(1) # simulate work
        mark_completed(TriageOutput(
            category=CategoryEnum.other,
            urgency=UrgencyEnum.normal,
            confidence=1.0,
            reason="Stub mode enabled."
        ))
        return
        
    if os.environ.get("LLM_ENABLED") == "false":
        mark_failed("LLM features are currently disabled via kill switch.")
        return
        
    try:
        with open("prompts/triage-v1.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except Exception as e:
        mark_failed(f"Failed to load prompt: {str(e)}")
        return
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": payload_text}
    ]
    
    def call_model(msgs):
        start_time = time.time()
        res = llm_client.chat.completions.create(
            model=os.environ.get("LLM_MODEL", "openrouter/free"),
            messages=msgs,
            temperature=0.0
        )
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Cost logging
        with open("logs/cost.jsonl", "a", encoding="utf-8") as cost_f:
            cost_f.write(json.dumps({
                "prompt_version": "v1",
                "model": os.environ.get("LLM_MODEL", "openrouter/free"),
                "input_tokens": res.usage.prompt_tokens if res.usage else 0,
                "output_tokens": res.usage.completion_tokens if res.usage else 0,
                "duration_ms": duration_ms
            }) + "\n")
            
        return res.choices[0].message.content
        
    try:
        raw_output = call_model(messages)
    except Exception as network_e:
        mark_failed(f"LLM provider took too long or failed: {str(network_e)}")
        return
        
    # Parse and repair loop
    try:
        clean_json = raw_output.strip().removeprefix("`json").removesuffix("`").strip()
        data = json.loads(clean_json)
        validated = TriageOutput(**data)
        mark_completed(validated)
    except (json.JSONDecodeError, ValidationError) as e:
        # Repair once
        repair_msg = f"Your previous answer was rejected for this reason: {str(e)}. Return only corrected JSON matching the schema."
        messages.append({"role": "assistant", "content": raw_output})
        messages.append({"role": "user", "content": repair_msg})
        
        try:
            repaired_output = call_model(messages)
        except Exception as network_e:
            mark_failed(f"LLM provider took too long or failed during repair: {str(network_e)}")
            return
             
        try:
            clean_json = repaired_output.strip().removeprefix("`json").removesuffix("`").strip()
            data = json.loads(clean_json)
            validated = TriageOutput(**data)
            mark_completed(validated)
        except Exception as repair_e:
            with open("logs/quarantine.jsonl", "a", encoding="utf-8") as log_f:
                log_f.write(json.dumps({
                    "input": payload_text,
                    "prompt_version": "v1",
                    "raw_output": repaired_output,
                    "error": str(repair_e)
                }) + "\n")
            mark_failed(f"Failed to generate valid output: {str(repair_e)}")

@app.post("/triage", summary="Triage Support Message (Background)", status_code=202)
async def triage_message_background(payload: TriageInput, background_tasks: BackgroundTasks):
    # Idempotency check
    idemp_key = payload.idempotency_key
    if not idemp_key:
        # Fallback to hashing the payload if no explicit key is provided
        idemp_key = hashlib.sha256(payload.text.encode('utf-8')).hexdigest()
        
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id, status FROM triage_jobs WHERE idempotency_key = %s", (idemp_key,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return {"job_id": existing["id"], "status": existing["status"], "message": "Job already exists."}
        
    job_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO triage_jobs (id, idempotency_key, status) VALUES (%s, %s, %s)",
        (job_id, idemp_key, "pending")
    )
    conn.commit()
    conn.close()
    
    background_tasks.add_task(process_triage_job, job_id, payload.text)
    return {"job_id": job_id, "status": "pending"}

@app.get("/triage/{job_id}", summary="Get Triage Job Status", response_model=TriageJobResponse)
async def get_triage_status(job_id: str):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM triage_jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    result = None
    if job["status"] == "completed":
        result = TriageOutput(
            category=job["category"],
            urgency=job["urgency"],
            confidence=job["confidence"],
            reason=job["reason"]
        )
        
    return TriageJobResponse(
        job_id=job["id"],
        status=JobStatusEnum(job["status"]),
        result=result,
        error=job["error"]
    )


# --- Inngest Integration ---
from inngest.fastapi import serve
from src.inngest_app.client import inngest_client
from src.inngest_app.functions import ai_flow_execution
import inngest

inngest_route = serve(inngest_client, [ai_flow_execution])
app.add_route("/api/inngest", inngest_route, methods=["GET", "POST", "PUT"])

# Endpoint to trigger the flow from frontend
from pydantic import BaseModel
class FlowRunRequest(BaseModel):
    nodes: dict
    start_node_id: str

@app.post("/api/flow/run")
async def trigger_flow(req: FlowRunRequest):
    await inngest_client.send(
        inngest.Event(
            name="ai/flow.run",
            data={
                "nodes": req.nodes,
                "start_node_id": req.start_node_id
            }
        )
    )
    return {"status": "Flow triggered via Inngest"}


# --- PDF Report Generator Endpoint ---
from fpdf import FPDF
from datetime import datetime

class ReportJobResponse(BaseModel):
    job_id: str
    status: str
    download_url: Optional[str] = None
    error: Optional[str] = None

def generate_pdf_report(job_id: str):
    try:
        conn = get_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Mark as processing
        cursor.execute("UPDATE report_jobs SET status = 'processing' WHERE id = %s", (job_id,))
        conn.commit()
        
        # 1. Fetch data
        cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN done THEN 1 ELSE 0 END) as completed FROM tasks")
        task_stats = cursor.fetchone()
        
        cursor.execute("SELECT category, count(*) as count FROM triage_jobs WHERE status='completed' GROUP BY category")
        triage_stats = cursor.fetchall()
        
        # 2. Render PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "System Health & Data Report", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 10, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(10)
        
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "1. Tasks Overview", ln=True)
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 10, f"Total Tasks: {task_stats['total'] or 0}", ln=True)
        pdf.cell(0, 10, f"Completed Tasks: {task_stats['completed'] or 0}", ln=True)
        pdf.ln(10)
        
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "2. LLM Triage Statistics", ln=True)
        pdf.set_font("helvetica", "", 12)
        if not triage_stats:
            pdf.cell(0, 10, "No triage jobs found.", ln=True)
        else:
            for row in triage_stats:
                pdf.cell(0, 10, f"Category '{row['category']}': {row['count']} requests", ln=True)
                
        # Save PDF
        filepath = f"static/reports/report_{job_id}.pdf"
        pdf.output(filepath)
        
        # 3. Update job as completed
        download_url = f"/static/reports/report_{job_id}.pdf"
        cursor.execute("UPDATE report_jobs SET status = 'completed', download_url = %s WHERE id = %s", (download_url, job_id))
        conn.commit()
        conn.close()
        
    except Exception as e:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE report_jobs SET status = 'failed', error = %s WHERE id = %s", (str(e), job_id))
        conn.commit()
        conn.close()

@app.post("/reports/generate", summary="Generate System Report (Background)", status_code=202)
async def trigger_report(background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO report_jobs (id, status) VALUES (%s, %s)",
        (job_id, "pending")
    )
    conn.commit()
    conn.close()
    
    background_tasks.add_task(generate_pdf_report, job_id)
    return {"job_id": job_id, "status": "pending"}

@app.get("/reports/{job_id}", summary="Get Report Job Status", response_model=ReportJobResponse)
async def get_report_status(job_id: str):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM report_jobs WHERE id = %s", (job_id,))
    job = cursor.fetchone()
    conn.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return ReportJobResponse(
        job_id=job["id"],
        status=job["status"],
        download_url=job["download_url"],
        error=job["error"]
    )
