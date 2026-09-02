import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_MARKET_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_MARKET_API_KEY not found in .env"
    )

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

models = client.models.list()

print("\n========================================")
print("MODELS AVAILABLE TO MARKET API KEY")
print("========================================\n")

for model in models.data:
    print(model.id)

print("\n========================================")
print(f"TOTAL MODELS: {len(models.data)}")
print("========================================")