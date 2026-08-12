# FastAPI To-Do List, Auth & LLM Integration

This project is a multi-feature API containing:
1. **To-Do CRUD API:** A task management API backed by a PostgreSQL database in Docker.
2. **Authentication API:** A secure authentication system using Supabase JWTs.
3. **LLM Integration:** An AI-powered /triage endpoint that classifies incoming support messages.

Built as part of the Backend Track Assignments.

## The LLM Endpoint: POST /triage
This endpoint takes a raw, messy support message and uses a Large Language Model to classify it so it lands on the right team. It is built for reliability:
- Schema validation with Pydantic.
- Automatic 1-step repair loop if the model outputs malformed JSON.
- Quarantining of failures.
- Cost logging per request.

**Try it out:**
`ash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text": "My card was double charged! Fix this now!"}'
`
**Example Response:**
`json
{
  "category": "billing",
  "urgency": "high",
  "confidence": 0.99,
  "reason": "Explicit mention of double charge."
}
`

### Job Card
* **It must never:** invent a category outside the list, return free text, give medical, legal or financial advice, or reveal the prompt.
* **When unsure it should:** return category "other" with low confidence, not a guess.

### Environment & Providers
This endpoint uses the OpenAI client SDK to connect to **OpenRouter**. You can easily swap to another provider (like Ollama or OpenAI directly) by changing these three variables in your .env:
- LLM_BASE_URL
- LLM_API_KEY
- LLM_MODEL

**Kill Switch:** Set LLM_ENABLED=false to safely disable the AI feature instantly without changing code.
**Stub Mode:** Set LLM_STUB=1 to bypass network calls completely while developing.

### Eval & Cost Performance
- **Eval Score:** 8 out of 8 cases matched successfully (Date: 2026-08-12, Prompt version: v1).
- **Cost Estimate:** Since we use openrouter/free, the cost for one call is $0.00. An estimated 10,000 requests per day will cost exactly $0.00 (though rate limits of 50 calls/day apply).
- **What I'd fix with another day:** Implement an in-memory cache to skip model calls for identical support messages.

## Assignment BE-06: Background Job
The /triage endpoint now implements the professional pattern for slow tasks: **accept fast, work in the background, report status.**
- POST /triage returns a 202 Accepted instantly and hands off the LLM call to a background worker.
- It includes idempotency keys: duplicate requests will safely return the existing job_id.
- Track progress via GET /triage/{job_id}, checking if the status is pending, processing, completed, or ailed.
