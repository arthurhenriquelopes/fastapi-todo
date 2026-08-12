# The Through-Line: Map Content & CTAs

**Track:** General AI Fluency  

---

## 1. The One-Line Claim
*I used AI to brainstorm 10 options focusing on reliability and backend AI integration, then ruthlessly sharpened the best one into this final claim:*

> **"I engineer resilient Backend AI systems that scale securely, so your team doesn't wake up to unhandled LLM exceptions at 3 AM."**

## 2. The Content Map (Home Page)
*The portfolio is structured as a single, high-impact scroll. Every section points the visitor toward the final goal: verifying my code and hiring me.*

**Section 1: The Hero**
- **Content:** The One-Line Claim + Accepted Hero Texture (Slate/Electric Blue).
- **CTA:** "See the Architecture" (Anchors down to the flagship case).

**Section 2: The Flagship Case Study (Lead with the strongest)**
- **Which Case:** AI-Powered Customer Support Triage System.
- **Content:** The problem (blocking main threads), my decisions (Supabase, Inngest, JSON Repair Loop), and the outcome (202 Accepted milliseconds latency).
- **Visuals:** React Flow UI Mockup + LLM Architecture Diagram.
- **CTA:** "Read the full case study" (Expands the text).

**Section 3: The Toolkit & Secondary Case**
- **Which Case:** The Polite Scraper (Data Pipeline).
- **Content:** How I built a robust, rate-limited python scraper using Pydantic validation.
- **Visuals:** Swagger UI & Database Screenshots.
- **CTA:** "View the raw scraping logic."

**Section 4: The Bio**
- **Content:** The "Voice Card" bio, stating my focus on latency and fault tolerance.
- **Visuals:** Professional Headshot.

**Section 5: The Ultimate Call To Action (Laddering up to the Week 1 Goal)**
- **The Action:** The entire page exists to get the engineering manager or recruiter to look at my actual code and validate my skills.
- **Final CTA:** **"Review the complete Monorepo on GitHub."**

## 3. The "Still Need to Gather" List
*To finish the portfolio build without getting blocked, I still need to collect:*

1. **A Professional Headshot:** I need to take a clean, well-lit photo for the Bio section.
2. **Live Demo URL:** The project currently runs on docker-compose locally. I need to gather a live deployment link (e.g., Render, Fly.io, or AWS) so the recruiter can hit the endpoints without cloning the repo.
3. **Before/After Performance Numbers:** I need to benchmark the /triage endpoint to show the exact latency drop (in milliseconds) achieved by moving the LLM call from the main thread into a Background Job.
