# Agent Concepts and MCP Basics

**Track:** General AI Fluency  

---

## 1. Workflow vs. Agent

The term "Agent" is highly abused in marketing, often used to describe simple automations. According to Anthropic's canonical *Building Effective Agents*, the distinction is fundamentally about **autonomy and control flow**.

**A Workflow** is a rigid, deterministic pipeline orchestrated by humans. The developer defines the steps, the sequence, and the logic. The AI is merely a passenger executing a specific prompt at a specific stage (e.g., "Take input A and summarize it, then pass it to Step 2"). It thinks in a straight line.

**An Agent**, on the other hand, is goal-driven and autonomous. The human defines the objective and provides a set of tools, but the AI itself dynamically decides *which* tools to use, *when* to use them, and *how* to react to errors. It operates in a continuous loop of reasoning (Observe ? Think ? Act) until the goal is achieved.

**Classifying FL-04:**
My FL-04 project (The API Documentation Generator) is strictly a **Workflow**, not an agent. It follows a hardcoded chain (Draft ? Critique ? Revise). The LLM cannot decide to skip the critique step, nor can it decide to go search the web for missing context. It is a highly efficient pipeline, but it lacks autonomy.

---

## 2. What is MCP? (Model Context Protocol)

If an LLM is a brain in a jar, **MCP (Model Context Protocol)** is its nervous system. Described perfectly as the "USB-C port for AI," MCP is an open standard that allows AI models to securely connect to external tools, data sources, and environments.

Before MCP, if you wanted Claude to read your local database and also check your Slack messages, developers had to build custom API integrations for each service. With MCP, anyone can build a standardized "Server" (e.g., a Postgres MCP Server). Any AI application that supports the protocol can instantly plug into that server, discovering its available **Prompts** (templates), **Resources** (data like files or logs), and **Tools** (actions the AI can execute, like querying a table).

It solves the fragmentation of AI integration, giving models universal "hands and eyes."

---

## 3. Evolving FL-04 into a True Agent

To evolve my static FL-04 documentation pipeline into a true Agent, I would have to tear down the rigid 3-step chain and change the architecture:

1. **The Goal:** Instead of feeding it one piece of code at a time, I would give the AI a high-level goal: *"Ensure all FastAPI routes in this repository have up-to-date markdown documentation."*
2. **The Tools (Via MCP):** I would connect the AI to an MCP server providing local system tools: list_directory, ead_file, write_to_file, and un_git_commit.
3. **The Autonomous Loop:** I would hit "Start". The agent would autonomously use list_directory to explore my project. It would use ead_file to analyze main.py. It would realize 5 endpoints are undocumented. It would draft the docs in its "scratchpad", review them against OpenAPI standards, and finally use write_to_file to save the markdown and un_git_commit to push the code. It controls its own execution path until the job is done.

---

## 4. MCP Connector Evidence: 3 Tasks Chat Alone Could Not Do

*As part of this assignment, I utilized an MCP-powered Agent (Antigravity) operating directly inside my local IDE. Below are three distinct tasks it executed via MCP tools, which a standard ChatGPT web interface is physically incapable of doing:*

1. **Local File System Mutation (write_to_file):** The agent autonomously wrote this exact markdown file directly to my local hard drive inside the General-AI-Fluency folder without me copy-pasting anything.
2. **Executing Terminal Commands (un_command):** The agent executed git add, git commit, and git push origin main directly in my Windows PowerShell via an MCP tool call to sync my portfolio to GitHub.
3. **Generating and Saving Local Assets (generate_image):** The agent generated a mockup screenshot of a smartphone and saved the binary .jpg file directly into my local ssets/ folder, referencing it automatically in the markdown.

*(Screenshots of these tool calls executing in the Agent's interface are attached to the assignment submission).*
