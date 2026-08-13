import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class SRETriagerAgent:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
    def fetch_sentry_errors(self, project_id: str):
        """Simulates fetching the latest error from Sentry."""
        print(f"🔧 Tool Call: fetch_sentry_errors(project={project_id})")
        # In a real app, this would be: requests.get("https://sentry.io/api/0/projects/...")
        return {
            "error_type": "KeyError",
            "message": "'JWT_SECRET'",
            "file": "auth.py",
            "timestamp": "2026-08-13T10:00:00Z"
        }
        
    def fetch_recent_commits(self, repo: str):
        """Fetches REAL recent commits from GitHub."""
        print(f"🔧 Tool Call: fetch_recent_commits(repo={repo})")
        url = f"https://api.github.com/repos/{repo}/commits"
        response = requests.get(url)
        if response.status_code == 200:
            commits = response.json()[:3]
            return [{"sha": c["sha"][:7], "message": c["commit"]["message"], "author": c["commit"]["author"]["name"]} for c in commits]
        return [{"error": "Could not fetch commits"}]

    def draft_slack_report(self, message: str, confidence: int):
        """Drafts a slack report and saves it locally instead of hitting a real webhook (to avoid spam)."""
        print(f"🔧 Tool Call: draft_slack_report(confidence={confidence}%)")
        report = f"🚨 SRE TRIAGE REPORT 🚨\n\n{message}\n\nConfidence: {confidence}%"
        if confidence < 70:
            report += "\n⚠️ [LOW CONFIDENCE - VERIFY MANUALLY]"
            
        with open("incident_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("✅ Report written to incident_report.md")
        return "Success"

    def execute_loop(self):
        print("🤖 Starting SRE Triager Agent Loop...")
        
        system_prompt = (
            "You are an elite Site Reliability Engineering Assistant. "
            "You have access to 3 tools: fetch_sentry_errors, fetch_recent_commits, and draft_slack_report. "
            "When an incident starts, fetch the errors for project 'fastapi-todo', then fetch commits for 'arthurhenriquelopes/fastapi-todo'. "
            "Correlate the error with the commits. Draft a slack report summarizing the root cause. "
            "IMPORTANT: Always return tool calls until you draft the report."
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "fetch_sentry_errors",
                    "description": "Get the latest backend errors from Sentry.",
                    "parameters": {
                        "type": "object",
                        "properties": {"project_id": {"type": "string"}},
                        "required": ["project_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_recent_commits",
                    "description": "Get the latest 3 commits from a GitHub repository.",
                    "parameters": {
                        "type": "object",
                        "properties": {"repo": {"type": "string"}},
                        "required": ["repo"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "draft_slack_report",
                    "description": "Send a formatted incident report to the team.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "The root cause analysis"},
                            "confidence": {"type": "integer", "description": "0 to 100 confidence score"}
                        },
                        "required": ["message", "confidence"]
                    }
                }
            }
        ]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Alert: We are seeing a spike in 500 errors in production. Investigate it."}
        ]
        
        # Max 5 turns to prevent infinite loops
        for turn in range(5):
            payload = {
                "model": "openai/gpt-4o-mini",
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto"
            }
            
            print(f"\n[Turn {turn + 1}] Thinking...")
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=self.headers, json=payload)
            response_data = response.json()
            
            message = response_data["choices"][0]["message"]
            messages.append(message)
            
            if message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    func_name = tool_call["function"]["name"]
                    args = json.loads(tool_call["function"]["arguments"])
                    
                    if func_name == "fetch_sentry_errors":
                        result = self.fetch_sentry_errors(**args)
                    elif func_name == "fetch_recent_commits":
                        result = self.fetch_recent_commits(**args)
                    elif func_name == "draft_slack_report":
                        result = self.draft_slack_report(**args)
                    else:
                        result = "Unknown function"
                        
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": func_name,
                        "content": json.dumps(result)
                    })
            else:
                print(f"\n🎯 Agent Final Response:\n{message.get('content', 'Done.')}")
                break

if __name__ == "__main__":
    agent = SRETriagerAgent()
    agent.execute_loop()
