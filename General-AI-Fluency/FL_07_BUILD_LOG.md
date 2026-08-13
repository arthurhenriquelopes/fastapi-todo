# FL-07: Build Log - The SRE Triager Agent

**Track:** General AI Fluency  
**Phase:** Build (Week 5)  

## 1. What was Built
I implemented the `SRETriagerAgent` as a Python script (`src/agent/sre_triager.py`) that uses the OpenRouter API to orchestrate tool calls. The agent is designed to run in a loop, fetching data, correlating it, and drafting a report.

## 2. Live Tool Connections
The agent successfully uses **Function Calling (Tools)** to interface with the outside world:
1. **GitHub API (Live Data Source):** The `fetch_recent_commits` tool uses the real GitHub REST API (`https://api.github.com/repos/...`) to fetch the exact commits made to the `fastapi-todo` repository. This proves the agent can read external live state.
2. **Sentry (Mocked):** Due to time constraints and lack of a live Sentry project with active errors, `fetch_sentry_errors` simulates an API response returning a `KeyError` in `auth.py`.
3. **Slack (File System Output):** To prevent spamming a real Slack workspace, the `draft_slack_report` tool was slightly modified to write the markdown report directly to a local file (`incident_report.md`).

## 3. What Broke & What I Changed
- **Deviation from Spec (PydanticAI):** The original spec proposed using `PydanticAI`. However, during the build, I decided to use **raw OpenAI Function Calling via `requests`** to keep the agent extremely lightweight, removing the need for heavy frameworks like LangChain or PydanticAI. This teaches the raw fundamentals of how the LLM actually outputs JSON to trigger functions.
- **Handling Infinite Loops:** Early runs of agent loops can sometimes get stuck calling the same tool repeatedly if the prompt isn't clear. I added a hard limit (`for turn in range(5):`) to enforce the "Kill Switch" guardrail defined in the FL-06 spec.

## 4. Successful End-to-End Run
When run, the agent executed the following reasoning trace:
1. **Turn 1:** Called `fetch_sentry_errors(project_id="fastapi-todo")` and `fetch_recent_commits(repo="arthurhenriquelopes/fastapi-todo")` simultaneously.
2. **Turn 2:** Read the JSON responses. Noticed a `KeyError: 'JWT_SECRET'` in `auth.py`. Correlated it with the recent commits fetched from the live GitHub repository.
3. **Turn 3:** Called `draft_slack_report(message=..., confidence=...)`.
4. **Turn 4:** Output the final "Done" message and exited gracefully.

The final report was successfully written to disk, completely bypassing the need for human intervention.
