# Three Roads: Choose Your Stack

**Track:** General AI Fluency  

---

## 1. The Constraints (Given to AI)
- **Budget:** 100% Free.
- **Skill Level:** Backend AI Engineer (Strong in Python/FastAPI/Docker, comfortable in React/JS).
- **Content Needs:** A Hero section, Case Studies (Triage API, Polite Scraper), and a Bio.
- **Display Needs:** Must elegantly display raw code blocks, architecture diagrams, Swagger screenshots, and ideally embed the interactive React Flow AI node graph we built in the backend track. No dynamic database needed yet.

## 2. The AI's 3 Stack Options

### Option 1: The Simplest (GitHub Pages + Markdown / Jekyll)
- **How I'd build:** Write pure Markdown files and let Jekyll compile them.
- **Host:** GitHub Pages (Free).
- **Backend needed?** No.
- **Trade-off:** Extremely fast to write, but highly rigid. I cannot embed my interactive React Flow nodes easily, and styling is limited.

### Option 2: The Sweet Spot (React/Vite + Tailwind CSS)
- **How I'd build:** Build a static Single Page Application (SPA) using React and Tailwind.
- **Host:** Vercel or Netlify (Free).
- **Backend needed?** No (Static export).
- **Trade-off:** Slower to write text than Markdown, but gives total freedom over the UI and allows embedding complex interactive components.

### Option 3: The Most Powerful (Full-Stack Next.js + FastAPI + Postgres)
- **How I'd build:** Next.js frontend fetching dynamic case studies from a Live FastAPI backend.
- **Host:** Vercel (Frontend) + Render/Fly.io (Backend).
- **Backend needed?** Yes.
- **Trade-off:** Massive overkill. Free-tier databases go to sleep causing 30-second cold starts. Maintenance is a nightmare for content that rarely changes.

---

## 3. My Final Decision & Rationale

**Chosen Stack:** Option 2 (React/Vite or Next.js Static on Vercel).

**Why I chose it over the others:**
I rejected Option 1 (GitHub Pages/Markdown) because it fails my display constraint: I want to embed the actual **React Flow AI UI** I built during the Backend track directly into the page to wow the recruiter. Markdown can't do that natively. 

I rejected Option 3 (Full-Stack) because of the maintenance trap. *Can I maintain this?* No. A live backend for a portfolio means dealing with free-tier server sleeping, database migrations, and security patches just to serve static text. It violates the "Decide Once" philosophy.

**The Sweet Spot (Option 2)** gives me exactly what I need: it perfectly displays my work (code blocks and React Flow embeds), costs  on Vercel, and because it has no backend database, I can deploy it once and never worry about it crashing while I'm sleeping. 

*(Note: I already have a foundation for this in my rthur-portfolio repository, which perfectly aligns with this architectural decision!)*
