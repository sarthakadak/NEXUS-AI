import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    raise ValueError("NVIDIA_API_KEY not found in .env")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

response = client.chat.completions.create(
    model="nvidia/nemotron-3.5-lightning-30b-a3b",
    messages=[
        {
            "role": "system",
            "content": "You are a technical feasibility assistant."
        },
        {
            "role": "user",
            "content": "In one sentence, explain whether installing EV charging stations is technically feasible."
        }
    ],
    temperature=0,
    max_tokens=200,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    }
)

print("\n===== NEMOTRON TEST =====")
print(response.choices[0].message.content)
print("==========================")