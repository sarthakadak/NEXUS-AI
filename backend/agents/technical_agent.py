from agents.llm_client import call_llm_json

TECHNICAL_SYSTEM_PROMPT = """
You are the Technical Feasibility Agent in a multi-agent AI system.

Your job is to analyze ONLY the technical aspects of the user's problem.

You must identify:

- Technical facts explicitly provided by the user
- Missing technical information
- Technical assumptions
- Hardware requirements
- Software requirements
- Infrastructure requirements
- Technical complexity
- Scalability
- Technical risks
- Technical recommendation
- Confidence level

IMPORTANT RULES:

1. Never invent user-provided facts.
2. Never invent numerical values.
3. Clearly distinguish facts from assumptions.
4. If information is missing, report it under missing_information.
5. Do not perform financial analysis.
6. Do not perform market analysis.
7. Do not make legal or medical decisions.
8. Do not make the final overall decision.
9. Return ONLY valid JSON.
10. Do not use Markdown.
11. Keep the response concise.
"""


def analyze_technical(problem: str) -> dict:

    prompt = f"""
Analyze ONLY the technical feasibility of the following problem.

USER PROBLEM:

{problem}

Return ONLY valid JSON using EXACTLY this structure:

{{
    "technical_overview": "",
    "missing_information": [],
    "assumptions": [],
    "hardware_requirements": [],
    "software_requirements": [],
    "infrastructure_requirements": [],
    "technical_complexity": "",
    "scalability": "",
    "technical_risks": [],
    "recommendation": "",
    "confidence": ""
}}

STRICT RULES:

- Use only user-provided information as facts.
- Do not invent facts.
- Do not invent numerical values.
- Missing technical information goes into missing_information.
- Assumptions must be clearly identified as assumptions.
- Hardware requirements can include necessary technical components,
  but do not claim that the user already has them.
- Software requirements can include necessary software/control systems,
  but do not claim that the user already has them.
- Infrastructure requirements can include necessary infrastructure.
- Do not perform financial calculations.
- Do not perform market analysis.
- Maximum 5 items in each list.
- Keep each list item concise.
- Keep text concise.
- Return JSON only.
"""

    analysis = call_llm_json(
        "technical",
        TECHNICAL_SYSTEM_PROMPT,
        prompt,
        max_tokens=1500
    )

    return {
        "domain": "technical",
        "user_provided_data": {
            "problem": problem
        },
        "technical_overview": analysis.get("technical_overview", ""),
        "missing_information": analysis.get("missing_information", []),
        "assumptions": analysis.get("assumptions", []),
        "hardware_requirements": analysis.get("hardware_requirements", []),
        "software_requirements": analysis.get("software_requirements", []),
        "infrastructure_requirements": analysis.get("infrastructure_requirements", []),
        "technical_complexity": analysis.get("technical_complexity", ""),
        "scalability": analysis.get("scalability", ""),
        "technical_risks": analysis.get("technical_risks", []),
        "recommendation": analysis.get("recommendation", ""),
        "confidence": analysis.get("confidence", "")
    }