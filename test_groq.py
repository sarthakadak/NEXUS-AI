import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are a financial feasibility assistant."
        },
        {
            "role": "user",
            "content": (
                "A college wants to install 10 EV charging stations. "
                "Each station costs $5,000. Installation costs $1,000 per station. "
                "Annual electricity cost is $8,000. Annual maintenance cost is $2,000. "
                "Charging is free, so there is no revenue. "
                "In one sentence, state whether this is financially feasible."
            )
        }
    ],
    temperature=0,
    max_tokens=300
)

print("\n===== GROQ FINANCE TEST =====")
print(response.choices[0].message.content)
print("=============================")