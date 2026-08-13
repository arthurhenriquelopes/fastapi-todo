# Ship an Automation Workflow v2

**Track:** General AI Fluency  
**Pipeline Chosen:** API Documentation Generator (Draft ? Critique ? Revise)

---

## 1. The Workflow Diagram
*I designed this pipeline to automate the tedious process of writing OpenAPI/Swagger documentation for my backend routes. It uses a chained prompt approach (Prompt Chaining) inside a Claude Project/Custom GPT.*

`mermaid
graph TD
    A[Raw Python Route Code] --> B(Step 1: Draft)
    B --> |Rough Markdown Spec| C(Step 2: Critique)
    C --> |Feedback on missing edge cases| D(Step 3: Revise & Format)
    D --> E[Final Production-Ready API Doc]
`

## 2. Prompts & Configuration
Instead of one massive prompt that confuses the LLM, I broke it into three distinct chained prompts (No-Code approach via Claude Projects):

**Step 1 Prompt (Draft):**  
> *"Analyze this raw FastAPI Python code. Extract the HTTP method, route, input payload structure, and successful return schema. Output a rough bulleted list."*

**Step 2 Prompt (Critique):**  
> *"Act as a strict QA Engineer. Review the draft from Step 1. Identify missing edge cases, error codes (400, 401, 404, 500), and missing authentication headers based on the original code. Output a critique list."*

**Step 3 Prompt (Revise & Format):**  
> *"Merge the Draft and the Critique. Format the final output into a clean, markdown-based API documentation block, exactly as it would appear in a ReadMe or Swagger description."*

---

## 3. The 5 Real Runs

I ran this automation pipeline on five real endpoints from my astapi-todo monorepo.

### Run 1: GET /tasks
- **Input:** Raw code for fetching all tasks via psycopg2.
- **Output:** Clean Markdown table showing response schema List[Task] and a note that it returns [] if empty. No errors found in critique.

### Run 2: POST /tasks
- **Input:** Raw code for task creation.
- **Output:** Documented TaskCreate payload. *Critique step caught that the title cannot be empty.* Revision added a 400 Bad Request schema to the docs.

### Run 3: PUT /tasks/{task_id}
- **Input:** Code for updating a task by ID.
- **Output:** Documented path parameter {task_id}. *Critique step caught the missing 404 exception.* Revision added 404 Not Found - Task {id} not found to the final spec.

### Run 4: POST /auth/login
- **Input:** Supabase JWT login route.
- **Output:** Documented the UserCredentials JSON requirement. *Critique step caught the exception block.* Revision added the 401 Unauthorized - Invalid login credentials error.

### Run 5: POST /triage
- **Input:** The flagship AI background job route.
- **Output:** Documented the TriageInput payload and 202 Accepted response. *Critique step caught the idempotency behavior.* Revision clearly documented that duplicate requests return the existing job_id instead of starting a new background task.

---

## 4. Time Accounting & ROI

- **Setup Time:** 20 minutes (Writing, testing, and refining the 3 chained prompts).
- **Manual Time:** Writing docs for 1 complex endpoint manually takes me ~12 minutes. For 5 endpoints: **60 minutes**.
- **Workflow Time:** Running the chain takes ~1 minute per endpoint. For 5 endpoints: **5 minutes**.
- **Time Saved:** **55 minutes** just on this small batch. For a real production API with 50+ routes, this workflow saves an entire day of manual labor.

## 5. Failure Points & Human Review
*Where it breaks and what a human must still check:*

1. **Business Logic Nuance:** The LLM knows *what* the code does, but sometimes misinterprets *why*. For example, on the /triage route, it didn't initially understand that the idempotency_key was a hash fallback, so a human (me) had to manually verify that paragraph.
2. **Database Triggers:** If an endpoint relies on a PostgreSQL trigger that isn't visible in the Python code, the LLM won't document it. A human must always cross-reference database side-effects.
