# The Prompt Ladder: From Lazy to Engineered

**Track:** General AI Fluency  
**Focus:** Backend Engineering (FastAPI)

---

## The Baseline
**The Prompt:**  
> "Write backend code for a todo app."

**The Output (Excerpt):**  
> *"Sure! Here is a simple backend using Node.js and Express. First, make sure you have npm installed. Run `npm init -y`, then `npm install express body-parser...` [Proceeds to generate 150 lines of generic JavaScript inside a single `server.js` file, using an in-memory array instead of a database]."*

**Notes:**
- **What changed:** Nothing. This is the baseline lazy prompt.
- **What actually improved:** N/A.
- **What still failed:** The model guessed the language (Node.js) instead of my stack (Python/FastAPI). It used an array instead of a real database, and it dumped a giant wall of beginner-level setup instructions.
- **What to try next:** Add real context about the tech stack.

---

## Version 1: Adding Real Context
**The Prompt:**  
> "Write a FastAPI backend for a todo app that connects to PostgreSQL."

**The Output (Excerpt):**  
> *"Here is your FastAPI application. [Generates a single `main.py` file with 200 lines of code. It uses `psycopg2` to write raw SQL strings like `cursor.execute("SELECT * FROM todos")` directly inside the route functions]."*

**Notes:**
- **What changed:** Added real context (Framework: FastAPI, DB: PostgreSQL).
- **What actually improved:** The output stopped generating JavaScript and gave me Python. It also actually attempted to connect to a database instead of using a fake array.
- **What still failed:** The architecture is a nightmare. It dumped all routes and database connections into one massive file, and raw SQL is prone to injection and hard to maintain.
- **What to try next:** Add constraints on how the code should be structured.

---

## Version 2: Adding Constraints
**The Prompt:**  
> "Write a FastAPI backend for a todo app that connects to PostgreSQL. Constraint: You must use SQLAlchemy as the ORM and organize the code into separate files for routers, models, and schemas."

**The Output (Excerpt):**  
> *"Great! Let's build a modular FastAPI app. First, create a file named `models.py`: [code block]... Next, create `schemas.py`: [code block]... Next, create `routers.py`... To run this, you will need to install `uvicorn`. Here is how you do it..."*

**Notes:**
- **What changed:** Added technical constraints (use SQLAlchemy, split into modular files).
- **What actually improved:** The code is finally production-ready. It used an ORM (SQLAlchemy) and cleanly separated the logic into `models.py`, `schemas.py`, and `routers.py`.
- **What still failed:** The output is extremely "chatty". It generated huge blocks of conversational filler and basic setup instructions that I have to manually scroll past to copy the code.
- **What to try next:** Specify an output format to kill the fluff.

---

## Version 3: Adding Output Format
**The Prompt:**  
> "Write a FastAPI backend for a todo app that connects to PostgreSQL. Constraint: You must use SQLAlchemy as the ORM and organize the code into separate files for routers, models, and schemas. Output format: Return ONLY the raw code blocks, prepended by their filename. Do not include any explanations, greetings, or setup instructions."

**The Output (Excerpt):**  
> `models.py`
> ```python
> class Todo(Base):
>     __tablename__ = "todos"
>     id = Column(Integer, primary_key=True)
>     title = Column(String)
> ```
> `routers.py`
> ```python
> @router.get("/{id}")
> def get_todo(id: int, db: Session = Depends(get_db)):
>     return db.query(Todo).filter(Todo.id == id).first()
> ```

**Notes:**
- **What changed:** Added a strict Output Format constraint.
- **What actually improved:** The annoying conversational filler vanished completely. I got exactly what I asked for: copy-pasteable files. 
- **What still failed:** By stripping away the conversational logic, the model generated the "happy path" code perfectly, but completely ignored edge cases. If a Todo ID isn't found, it just returns `null` instead of raising an HTTP 404 error.
- **What to try next:** Add quality criteria regarding error handling.

---

## Version 4: Adding Quality Criteria (The "Made it Worse" step)
**The Prompt:**  
> "Write a FastAPI backend for a todo app that connects to PostgreSQL. Constraint: You must use SQLAlchemy as the ORM and organize the code into separate files for routers, models, and schemas. Output format: Return ONLY the raw code blocks. Quality criteria: The code must include extremely robust error handling for every single database operation."

**The Output (Excerpt):**  
> ```python
> @router.get("/{id}")
> def get_todo(id: int, db: Session = Depends(get_db)):
>     try:
>         item = db.query(Todo).filter(Todo.id == id).first()
>         if item is None:
>             raise HTTPException(status_code=404, detail="Item not found")
>         return item
>     except SQLAlchemyError as e:
>         db.rollback()
>         raise HTTPException(status_code=500, detail="Database connection error occurred")
>     except Exception as e:
>         raise HTTPException(status_code=500, detail="Unknown error")
> ```

**Notes:**
- **What changed:** Added Quality Criteria demanding "extremely robust error handling".
- **What actually improved:** It successfully added HTTP 404 checks for missing items.
- **What made it worse:** This actually ruined the codebase. By demanding "extremely robust error handling", the AI overcompensated and wrapped *every single route* in massive `try/except` blocks catching base Exceptions. It bloated a 5-line route into 15 lines of defensive garbage that FastAPI handles natively anyway. 
- **What to try next:** Provide a specific example of what good, concise error handling looks like to fix the bloat.

---

## Version 5: Adding Examples of What Good Looks Like
**The Prompt:**  
> "Write a FastAPI backend for a todo app that connects to PostgreSQL. Constraint: You must use SQLAlchemy as the ORM and organize the code into separate files for routers, models, and schemas. Output format: Return ONLY the raw code blocks. Quality criteria: Handle HTTP 404s for missing records, but do not use broad try/except blocks. Example of good error handling style: `item = db.query(Model).filter(Model.id == id).first(); if not item: raise HTTPException(status_code=404, detail='Not found')`."

**The Output (Excerpt):**  
> ```python
> @router.get("/{id}")
> def get_todo(id: int, db: Session = Depends(get_db)):
>     todo = db.query(Todo).filter(Todo.id == id).first()
>     if not todo:
>         raise HTTPException(status_code=404, detail='Todo not found')
>     return todo
> ```

**Notes:**
- **What changed:** Replaced the vague quality criteria with a highly specific "Example of what good looks like".
- **What actually improved:** The bloat disappeared instantly. The AI followed the exact clean, concise pattern I provided. The code is now modular, silent (no filler), database-backed, and elegantly handles 404s without over-engineering.
- **What still failed:** Nothing. This prompt yields a perfect starting point for any CRUD entity.
- **What to try next:** Deploy to production!

---

## 🏆 Final Reusable Prompt
If someone on my backend team needs to generate boilerplates for new features, they can use this exact prompt:

> **Role:** You are an expert Python Backend Engineer.  
> **Task:** Write a FastAPI CRUD backend for a [INSERT ENTITY NAME] app that connects to PostgreSQL.  
> **Constraint:** You must use SQLAlchemy as the ORM and organize the code cleanly into separate files: `routers.py`, `models.py`, and `schemas.py`.  
> **Quality criteria:** Handle HTTP 404s for missing records, but do NOT wrap routes in broad try/except blocks. Rely on FastAPI's native exception handling.  
> **Example of good style:** `item = db.query(Model).filter(Model.id == id).first(); if not item: raise HTTPException(status_code=404, detail='Not found')`  
> **Output format:** Return ONLY the raw code blocks, prepended by their filename. Do not include any explanations, pleasantries, or setup instructions.
