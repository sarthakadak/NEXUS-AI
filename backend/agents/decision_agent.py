import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")

if not MODEL:
    raise ValueError("GEMINI_MODEL is not set.")

client = genai.Client(api_key=API_KEY)


DECISION_SYSTEM_PROMPT = """
You are the Final Decision Agent in a multi-agent AI
decision support system.

Your job is to synthesize the analyses provided by
the Finance, Technical, and Market agents.

You must:

- Compare the findings from all three agents.
- Identify agreements and conflicts between agents.
- Identify major strengths.
- Identify major concerns.
- Identify critical missing information.
- Determine the overall feasibility.
- Provide a final recommendation.
- Provide a confidence level.

IMPORTANT RULES:

1. Do NOT invent facts or data.
2. Do NOT ignore important risks identified by the domain agents.
3. Clearly distinguish known information from assumptions.
4. Do NOT perform new financial calculations.
5. Do NOT make legal, medical, or unrelated decisions.
6. Base the final decision ONLY on the information provided
   by the domain agents.
7. If critical information is missing, do not pretend that
   the project is definitely feasible or infeasible.
8. Before identifying anything as missing, cross-check ALL THREE
   domain-agent analyses. If the information is explicitly present
   in any agent analysis, it must NOT be listed as missing.
9. A missing detailed breakdown is NOT the same as missing information
   when a relevant total or aggregate value is already provided.
10. Only classify information as "critical_missing_information" when:
    - it is absent from all three domain-agent analyses, AND
    - its absence materially affects the feasibility decision.
11. Do not list information merely because having more detail would be
   useful. Useful validation items belong in the recommendation unless
   they are genuinely critical and currently unavailable.
12. The final decision may be:
   - Feasible
   - Conditionally Feasible
   - Not Feasible
   - Insufficient Information
13. Return ONLY valid JSON.
14. Do not use Markdown.
"""


def _call_gemini_json(prompt: str) -> dict:

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text[7:]

    if text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        print("\nERROR: Decision Agent returned invalid JSON.")
        print("\nRaw response:\n")
        print(text)
        raise


def make_final_decision(
    finance_analysis: dict,
    technical_analysis: dict,
    market_analysis: dict
) -> dict:

    decision_prompt = f"""
{DECISION_SYSTEM_PROMPT}

FINANCE AGENT ANALYSIS:

{json.dumps(finance_analysis, indent=2, ensure_ascii=False)}


TECHNICAL AGENT ANALYSIS:

{json.dumps(technical_analysis, indent=2, ensure_ascii=False)}


MARKET AGENT ANALYSIS:

{json.dumps(market_analysis, indent=2, ensure_ascii=False)}


Based ONLY on these three analyses, determine the
overall feasibility of the project.

Return ONLY valid JSON using EXACTLY this structure:

{{
    "overall_feasibility": "",
    "decision": "",
    "key_strengths": [],
    "key_concerns": [],
    "critical_missing_information": [],
    "agent_agreement": [],
    "agent_conflicts": [],
    "final_recommendation": "",
    "confidence": ""
}}

IMPORTANT:

- Do not invent information.
- Do not recalculate financial metrics.
- Consider Finance, Technical and Market findings equally.
- Cross-check all three analyses before declaring any information missing.
- Do not mark a component as missing when its total/aggregate value is
  already explicitly available in another agent's analysis.
- An explicitly provided aggregate annual operating expense is sufficient
  evidence that operating expenses are known. Do not classify maintenance,
  electricity, cloud, connectivity, support, or similar sub-components as
  missing merely because they are not separately itemized.
- If one agent explicitly says an aggregate operating expense covers named
  components, treat those components as known rather than missing.
- Only request a component-level breakdown if an agent explicitly indicates
  that the aggregate figure is incomplete, unreliable, or materially
  insufficient for the feasibility decision.
- Distinguish "critical missing information" from "information that would
  be useful to validate." Only the former belongs in the missing-information list.
- If critical information is missing, reflect that in the decision.
- The final recommendation must be supported by the three agent analyses.
"""

    result = _call_gemini_json(decision_prompt)

    return {
        "domain": "final_decision",

        "overall_feasibility":
            result.get(
                "overall_feasibility",
                ""
            ),

        "decision":
            result.get(
                "decision",
                ""
            ),

        "key_strengths":
            result.get(
                "key_strengths",
                []
            ),

        "key_concerns":
            result.get(
                "key_concerns",
                []
            ),

        "critical_missing_information":
            result.get(
                "critical_missing_information",
                []
            ),

        "agent_agreement":
            result.get(
                "agent_agreement",
                []
            ),

        "agent_conflicts":
            result.get(
                "agent_conflicts",
                []
            ),

        "final_recommendation":
            result.get(
                "final_recommendation",
                ""
            ),

        "confidence":
            result.get(
                "confidence",
                ""
            )
    }
