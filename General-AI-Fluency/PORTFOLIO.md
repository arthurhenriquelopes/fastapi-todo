# Voice Card
**"Direct, technical, passionate about solving problems, no fluff."**

---

# Case Study: AI-Powered Customer Support Triage System

### 1. The Problem
Customer support teams get flooded with unstructured messages, and humans waste hours just routing tickets to the right department. The naive solution is to build a chatbot to talk to the user, but chatbots often hallucinate and frustrate customers. The real technical challenge was building an AI system that doesn't talk to the user at all. It needed to act as a rigid, invisible router in the backend—and it had to process extremely slow LLM network calls without blocking the main FastAPI application thread.

### 2. What I Did (And What I Decided)
I didn't just wrap an OpenAI API call in a route; I engineered a resilient, asynchronous pipeline. 
- I built a **FastAPI** backend secured by **Supabase JWT** authentication.
- I shifted the slow AI classification out of the request lifecycle, delegating it to a background worker queue (using `FastAPI BackgroundTasks` and **Inngest**).
- I forced the LLM to output strict JSON, validated by **Pydantic** schemas.
- **Crucial Decision:** LLMs are unpredictable, so I implemented a self-healing **Repair Loop**. If the model hallucinates a bad JSON format or invents a category that doesn't exist, the system catches the exception and automatically re-prompts the model with the exact error, forcing it to fix its own mistake before returning the payload.
- I implemented **Idempotency Keys** so if a client accidentally spams the endpoint, the API deduplicates the request and doesn't waste LLM API quota.

### 3. The Outcome
A highly scalable triage endpoint (`POST /triage`) that returns a `202 Accepted` in milliseconds while the heavy lifting happens behind the scenes. The system achieved high accuracy on automated Evals (identifying bugs, billing issues, and feature requests). It is reliable, auditable (with token cost logging), fails gracefully via a deterministic Kill Switch, and even aggregates its data into automated PDF reports.

---

### Before & After: Killing the Fluff
**Generic AI Line (Before):** 
> *"I leveraged cutting-edge artificial intelligence to seamlessly optimize and transform the customer support experience, delivering results-driven value."*

**My Edited Line (After):** 
> *"I built an asynchronous LLM pipeline that rigidly classifies support tickets in the background, complete with a self-healing JSON repair loop."*

---

## Bio & Contact
Hi, I'm Arthur. I'm a Backend AI Engineer who builds systems that actually work in production, not just in tutorials. I care about latency, fault tolerance, and writing code that doesn't wake you up at 3 AM. 

[GitHub](https://github.com/arthurhenriquelopes) | [Email](mailto:arthurhenriquelopes@example.com)
