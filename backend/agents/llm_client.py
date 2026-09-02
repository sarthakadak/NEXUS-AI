"""
Multi-provider LLM client for the MAS project.

Finance    -> Groq -> GPT-OSS 20B
Technical  -> NVIDIA -> Nemotron 3.5 Lightning
Market     -> Groq -> Llama 3.3 70B

Decision Agent uses Gemini separately.
"""

import os
import json

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# API KEYS
# ============================================================

# Separate Groq keys for separate agents
GROQ_FINANCE_API_KEY = os.getenv("GROQ_FINANCE_API_KEY")
GROQ_MARKET_API_KEY = os.getenv("GROQ_MARKET_API_KEY")

# NVIDIA key for Technical Agent
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


# ============================================================
# CLIENTS
# ============================================================

groq_finance_client = None
groq_market_client = None
nvidia_client = None


# ============================================================
# GROQ - FINANCE
# ============================================================

if GROQ_FINANCE_API_KEY:

    groq_finance_client = OpenAI(
        api_key=GROQ_FINANCE_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )


# ============================================================
# GROQ - MARKET
# ============================================================

if GROQ_MARKET_API_KEY:

    groq_market_client = OpenAI(
        api_key=GROQ_MARKET_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )


# ============================================================
# NVIDIA - TECHNICAL
# ============================================================

if NVIDIA_API_KEY:

    nvidia_client = OpenAI(
        api_key=NVIDIA_API_KEY,
        base_url="https://integrate.api.nvidia.com/v1"
    )


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_CONFIGS = {

    # --------------------------------------------------------
    # FINANCE AGENT
    # --------------------------------------------------------

    "finance": {
        "provider": "groq_finance",
        "model": "openai/gpt-oss-20b",
    },


    # --------------------------------------------------------
    # TECHNICAL AGENT
    # --------------------------------------------------------

    "technical": {
        "provider": "nvidia",
        "model": "nvidia/nemotron-3.5-lightning-30b-a3b",
    },


    # --------------------------------------------------------
    # MARKET AGENT
    # --------------------------------------------------------

    "market": {
        "provider": "groq_market",
        "model": "qwen/qwen3.8-27b",
    },
}


# ============================================================
# JSON HELPERS
# ============================================================

def _strip_markdown_fences(text: str) -> str:

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def _extract_json(text: str) -> dict:

    cleaned = _strip_markdown_fences(text)

    # --------------------------------------------------------
    # Try complete response
    # --------------------------------------------------------

    try:

        return json.loads(cleaned)

    except json.JSONDecodeError:

        pass


    # --------------------------------------------------------
    # Try extracting JSON object
    # --------------------------------------------------------

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:

        candidate = cleaned[start:end + 1]

        return json.loads(candidate)


    raise json.JSONDecodeError(
        "No JSON object found in model response.",
        cleaned,
        0
    )


# ============================================================
# SINGLE PROVIDER CALL
# ============================================================

def _single_call(
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float
) -> str:

    # ========================================================
    # GROQ FINANCE
    # ========================================================

    if provider == "groq_finance":

        if groq_finance_client is None:

            raise RuntimeError(
                "GROQ_FINANCE_API_KEY is not configured."
            )

        client = groq_finance_client


    # ========================================================
    # GROQ MARKET
    # ========================================================

    elif provider == "groq_market":

        if groq_market_client is None:

            raise RuntimeError(
                "GROQ_MARKET_API_KEY is not configured."
            )

        client = groq_market_client


    # ========================================================
    # NVIDIA
    # ========================================================

    elif provider == "nvidia":

        if nvidia_client is None:

            raise RuntimeError(
                "NVIDIA_API_KEY is not configured."
            )

        client = nvidia_client


    # ========================================================
    # UNKNOWN PROVIDER
    # ========================================================

    else:

        raise ValueError(
            f"Unsupported provider: {provider}"
        )


    # ========================================================
    # BASE REQUEST
    # ========================================================

    request = {

        "model": model,

        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        "temperature": temperature,
    }


    # ========================================================
    # GROQ GPT-OSS SETTINGS
    # ========================================================

    if provider == "groq_finance" and model.startswith("openai/gpt-oss"):

        # GPT-OSS is a reasoning model.
        # max_completion_tokens includes reasoning + final output.

        request["max_completion_tokens"] = max(
            max_tokens,
            3000
        )

        request["reasoning_effort"] = "low"



    # ========================================================
    # OTHER MODELS
    # ========================================================

    else:

        request["max_tokens"] = max_tokens


    # ========================================================
    # NVIDIA NEMOTRON SETTINGS
    # ========================================================

    if provider == "nvidia":

        request["extra_body"] = {

            "chat_template_kwargs": {

                "enable_thinking": False

            }

        }


    # ========================================================
    # CALL MODEL
    # ========================================================

    response = client.chat.completions.create(
        **request
    )


    # ========================================================
    # VALIDATE CHOICES
    # ========================================================

    if not response.choices:

        raise RuntimeError(
            f"{provider}/{model} returned no choices."
        )


    # ========================================================
    # GET MESSAGE
    # ========================================================

    message = response.choices[0].message

    text = message.content


    # ========================================================
    # HANDLE EMPTY CONTENT
    # ========================================================

    if not text or not text.strip():

        # ----------------------------------------------------
        # GPT-OSS may sometimes place reasoning separately.
        # We do NOT use reasoning as the final JSON answer,
        # but provide a useful diagnostic.
        # ----------------------------------------------------

        reasoning = getattr(
            message,
            "reasoning",
            None
        )

        if reasoning:

            raise RuntimeError(
                f"{provider}/{model} returned reasoning "
                f"but no final content. "
                f"Reasoning tokens were generated without "
                f"a final response."
            )

        raise RuntimeError(
            f"{provider}/{model} returned empty content."
        )


    return text


# ============================================================
# CALL MODEL + JSON RETRY
# ============================================================

def _call_model_with_retry(
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float
) -> dict:

    # ========================================================
    # FIRST ATTEMPT
    # ========================================================

    raw = _single_call(

        provider=provider,

        model=model,

        system_prompt=system_prompt,

        user_prompt=user_prompt,

        max_tokens=max_tokens,

        temperature=temperature
    )


    # ========================================================
    # TRY JSON EXTRACTION
    # ========================================================

    try:

        return _extract_json(raw)

    except json.JSONDecodeError:

        print(
            f"WARNING: {provider}/{model} "
            f"returned invalid JSON."
        )

        print(
            "Retrying with JSON correction prompt..."
        )


    # ========================================================
    # JSON CORRECTION PROMPT
    # ========================================================

    correction_prompt = (

        "Your previous response was not valid JSON.\n"

        "Return ONLY the corrected valid JSON object.\n"

        "No Markdown.\n"

        "No code fences.\n"

        "No explanation.\n"

        "No extra text.\n\n"

        f"Previous response:\n{raw}"

    )


    # ========================================================
    # SECOND ATTEMPT
    # ========================================================

    raw_retry = _single_call(

        provider=provider,

        model=model,

        system_prompt=system_prompt,

        user_prompt=correction_prompt,

        max_tokens=max_tokens,

        temperature=temperature
    )


    # ========================================================
    # PARSE RETRY
    # ========================================================

    return _extract_json(raw_retry)


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def call_llm_json(
    agent_name: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2000,
    temperature: float = 0
) -> dict:

    # ========================================================
    # GET MODEL CONFIGURATION
    # ========================================================

    config = MODEL_CONFIGS.get(agent_name)


    if not config:

        raise ValueError(

            f"Unknown agent '{agent_name}'. "

            f"Available agents: "
            f"{list(MODEL_CONFIGS.keys())}"

        )


    provider = config["provider"]

    model = config["model"]


    # ========================================================
    # DISPLAY ROUTING
    # ========================================================

    print(

        f"[{agent_name}] Using "
        f"{provider} → {model}"

    )


    # ========================================================
    # CALL MODEL
    # ========================================================

    try:

        result = _call_model_with_retry(

            provider=provider,

            model=model,

            system_prompt=system_prompt,

            user_prompt=user_prompt,

            max_tokens=max_tokens,

            temperature=temperature

        )


        print(

            f"[{agent_name}] ✓ Response received"

        )


        return result


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        print(

            f"[{agent_name}] ✗ "
            f"{provider}/{model} failed"

        )

        print(

            f"Error: {type(e).__name__}: {e}"

        )


        raise RuntimeError(

            f"{agent_name} agent failed using "

            f"{provider}/{model}: {e}"

        ) from e