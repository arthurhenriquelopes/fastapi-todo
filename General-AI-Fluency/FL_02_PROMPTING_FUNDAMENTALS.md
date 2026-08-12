# FL-02: Prompting Fundamentals on Real Tasks v2

**Track:** General AI Fluency  
**Task Chosen:** Building "The Polite Scraper" (Assignment A9 from my Backend repo).

---

## 1. The Naive Baseline
**The Prompt:**  
> "Write a python web scraper for books.toscrape.com"

**The Output (Excerpt):**  
> *(Generates a basic script using `requests` and `BeautifulSoup`. It loops through the pages as fast as possible and prints the raw strings like `£51.77` to the terminal. Includes generic chatty text: "Here is your scraper! Make sure to install bs4...")*

**Notes:**
- **What changed:** This is the baseline.
- **What actually improved:** N/A.
- **What failed:** The code is completely irresponsible. It hammers the target server with zero delays (which would get us IP banned in production), and it doesn't clean the data (keeps the currency symbol mixed with the float).

---

## 2. Iteration 1: Role Assignment
**The Prompt:**  
> "**Act as a Senior Python Data Engineer.** Write a python web scraper for books.toscrape.com"

**The Output (Excerpt):**  
> *(Generates an Object-Oriented script with a `BookScraper` class, uses the `logging` module instead of `print()`, and adds type hints.)*

**Notes:**
- **What changed:** Added the "Role Assignment" technique.
- **What actually improved:** The structural quality of the code skyrocketed. The model shifted from writing a "tutorial script" to writing "production-grade" boilerplate (classes, type hints, logging).
- **What failed:** It still hammers the server with zero delays. A senior title didn't magically impart the specific business constraints of our task.

---

## 3. Iteration 2: Context and Motivation
**The Prompt:**  
> "Act as a Senior Python Data Engineer. Write a python web scraper for books.toscrape.com. **Context: This script will run daily as part of an automated pipeline. Our absolute highest priority is being a "polite" scraper so we never overwhelm the target server or trigger rate limits.**"

**The Output (Excerpt):**  
> *(The class now includes `time.sleep(2)` between requests, implements a Retry mechanism using `requests.adapters.HTTPAdapter` with `urllib3.util.Retry`, and sets a custom `User-Agent` header.)*

**Notes:**
- **What changed:** Added "Context and Motivation" to explain *why* we are building this.
- **What actually improved:** The logic changed drastically. By explaining the motivation (politeness/automation), the AI proactively added rate-limiting, custom headers, and network retry logic—solving the biggest architectural flaw.
- **What failed:** The scraped price data is still being returned as a dirty string (`"£51.77"`).

---

## 4. Iteration 3: Few-Shot Examples
**The Prompt:**  
> "Act as a Senior Python Data Engineer... [Context]... **Example of the exact data structure you must extract for each book: `{"title": "A Light in the Attic", "price": 51.77, "currency": "£"}`**."

**The Output (Excerpt):**  
> *(The code now imports `re` (regex) and parses the price string to separate the currency symbol from the float value before saving it to the dictionary.)*

**Notes:**
- **What changed:** Added a "Few-Shot Example" showing the exact expected output shape.
- **What actually improved:** The data cleaning problem was solved. By seeing the float `51.77` in the example, the AI implicitly understood that it needed to strip the currency symbol and cast the string, without me having to explicitly say "strip the pound sign".
- **What failed:** The code is starting to get messy. The scraping, cleaning, and saving logic are all crammed into one giant `scrape()` method.

---

## 5. Iteration 4: Step Decomposition
**The Prompt:**  
> "Act as a Senior Python Data Engineer... [Context & Example]... **Break the execution into these exact steps: Step 1: Fetch HTML with retries. Step 2: Parse raw strings. Step 3: Validate the dictionary using a Pydantic schema. Step 4: Save to a JSON file.**"

**The Output (Excerpt):**  
> *(The giant method is broken down. It creates a `BookSchema(BaseModel)` and distinct private methods: `_fetch_page()`, `_parse_book()`, `_validate_and_save()`.)*

**Notes:**
- **What changed:** Applied "Step Decomposition" to force architectural boundaries.
- **What actually improved:** The code is now modular and highly testable. Introducing Pydantic (because I explicitly broke it into a step) means our data pipeline is now strictly typed and safe.
- **What failed:** The AI still surrounds the perfect code with conversational fluff: *"Certainly! Here is how you can build this... let me know if you need help running it!"*

---

## 6. Iteration 5: Output Structure
**The Prompt:**  
> "Act as a Senior Python Data Engineer... [Context, Example, Steps]... **Output Structure: Return ONLY the raw, complete Python code block. Do not include any markdown greetings, explanations, or conclusions.**"

**The Output:**  
> *(Just the code block. Nothing else.)*

**Notes:**
- **What changed:** Added a strict "Output Structure" constraint.
- **What actually improved:** The output is now zero-friction. I can pipe this response directly into a `.py` file without manual editing.

---

## 7. Cross-Model Comparison (Claude 3.5 Sonnet vs. GPT-4o)

I ran the final engineered prompt through both leading models to compare their behaviors.

**Claude 3.5 Sonnet:**
- **Tone/Structure:** Obeyed the "Output Structure" constraint flawlessly. Zero conversational text.
- **Accuracy:** Claude leaned towards modern pythonic standards, opting to use `httpx` instead of `requests` for better async compatibility, and its Pydantic implementation was perfectly aligned with V2 syntax.
- **Failure points:** Sometimes Claude gets too clever and abstracts things into too many tiny helper functions, making the file slightly harder to read top-to-bottom.

**ChatGPT (GPT-4o):**
- **Tone/Structure:** Failed the "Output Structure" constraint slightly. It provided the code block perfectly but still couldn't resist adding a tiny *"Here is your complete script:"* at the top. 
- **Accuracy:** Wrote excellent, bulletproof `BeautifulSoup` parsing logic, specifically handling cases where DOM elements might be missing (`try/except AttributeError`). 
- **Comparison Conclusion:** Both generated production-ready code, but Claude is much better at strictly following negative constraints (like "do not talk"), whereas GPT-4o is slightly more defensive in its error handling logic.

---

## 8. Final Reusable Prompt Template

*You can use this template for generating any data pipeline or scraping task.*

> **Role:** Act as a Senior Python Data Engineer.  
> **Task:** Write a Python web scraper for [INSERT URL/TARGET].  
> **Context:** This script will run as part of an automated pipeline. Our absolute highest priority is being "polite" so we never overwhelm the target server or trigger rate limits. Implement retries, backoffs, and headers.  
> **Few-Shot Example:** For each item, extract the data to match exactly this schema: [INSERT JSON DICT EXAMPLE]. Make sure to clean raw strings into proper types (e.g., floats, ints) to match the example.  
> **Step Decomposition:** Break the execution into these exact steps: 
> 1. Fetch HTML with polite delays. 
> 2. Parse raw strings. 
> 3. Validate the dictionary using Pydantic. 
> 4. [INSERT STORAGE METHOD, e.g., Save to JSON / Insert to DB].  
> **Output Structure:** Return ONLY the raw, complete Python code block. Do not include any markdown greetings, explanations, or conclusions.
