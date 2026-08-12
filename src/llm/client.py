import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# We apply a real timeout of 30 seconds and let the SDK handle 429 and 5xx retries
llm_client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.environ.get("LLM_API_KEY", "sk-test"),
    timeout=30.0,
    max_retries=2
)
