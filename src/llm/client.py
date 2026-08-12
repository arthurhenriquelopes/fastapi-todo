import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

llm_client = OpenAI(
    base_url=os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.environ.get("LLM_API_KEY", "sk-test")
)
