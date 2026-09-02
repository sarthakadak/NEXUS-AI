from agents.llm_client import call_llm_json


# ============================================================
# MARKET AGENT SYSTEM PROMPT
# ============================================================

MARKET_SYSTEM_PROMPT = """
You are the Market and Business Feasibility Agent
in a multi-agent AI system.

Your job is to analyze ONLY the market and business
aspects of a problem.

You must identify:

- User-provided market information
- Target customers or users
- Market demand
- Competition
- Business model
- Market opportunities
- Missing market information
- Market assumptions
- Market constraints
- Growth potential
- Market risks
- Market recommendation
- Confidence level

IMPORTANT RULES:

1. Never invent user-provided market information.
2. Clearly distinguish facts, assumptions and estimates.
3. If market information is missing, report it.
4. Do not make financial calculations.
5. Do not make technical analysis.
6. Do not make legal or medical decisions.
7. Do not make the final overall decision.
8. Return ONLY valid JSON.
9. Do not use Markdown.
10. Keep the response concise.
"""


# ============================================================
# MARKET ANALYSIS
# ============================================================

def analyze_market(problem: str) -> dict:

    prompt = f"""
Analyze ONLY the market and business feasibility
of the following problem.

USER PROBLEM:

{problem}

Return ONLY valid JSON using EXACTLY this structure:

{{
    "market_overview": "",
    "target_customers": [],
    "market_demand": "",
    "competition": [],
    "business_model": "",
    "market_opportunities": [],
    "missing_information": [],
    "assumptions": [],
    "market_constraints": [],
    "market_risks": [],
    "growth_potential": "",
    "recommendation": "",
    "confidence": ""
}}

STRICT RULES:

1. Extract facts only from the USER PROBLEM.

2. target_customers:
   Include only customer groups explicitly mentioned
   or directly identifiable from the problem.

3. market_demand:
   Describe the stated demand or value proposition.
   If demand is not provided, say "Demand is unknown or unquantified."

4. competition:
   Include competitors only if explicitly provided.
   If competitors are not provided, return an empty list.

5. business_model:
   Describe the business model only using information
   provided in the problem.
   Do not invent pricing, revenue, subscriptions,
   commissions or other business terms.

6. market_overview:
   Give a short summary of the market/business situation
   based only on the user problem.

7. market_opportunities:
   Identify reasonable opportunities supported by the
   problem statement.
   Do not invent market sizes or statistics.

8. missing_information:
   Include only genuinely missing market/business information.

9. assumptions:
   Include assumptions that are necessary for market analysis.
   Clearly label them as assumptions.

10. market_constraints:
    Include constraints explicitly stated or directly implied
    by the problem.

11. market_risks:
    Identify reasonable market/business risks.
    Do not invent numerical values.

12. growth_potential:
    Describe growth potential qualitatively.
    Do not invent growth percentages or market sizes.

13. recommendation:
    Give ONLY a market/business recommendation.
    Do not give the final overall project decision.

14. confidence:
    Use one of:
    "High"
    "Medium"
    "Low"
    "Low to Medium"

15. Do NOT perform financial calculations.

16. Do NOT perform technical analysis.

17. Do NOT make the final overall decision.

18. Maximum 5 items in every list.

19. Keep every list item concise.

20. Keep every string under 40 words.

21. Return complete valid JSON.

22. No Markdown.
"""

    # ========================================================
    # CALL MARKET LLM
    # ========================================================

    analysis = call_llm_json(
        "market",
        MARKET_SYSTEM_PROMPT,
        prompt,
        max_tokens=2200
    )


    # ========================================================
    # NORMALIZE LIST FIELDS
    # ========================================================

    target_customers = analysis.get(
        "target_customers",
        []
    )

    competition = analysis.get(
        "competition",
        []
    )

    market_opportunities = analysis.get(
        "market_opportunities",
        []
    )

    missing_information = analysis.get(
        "missing_information",
        []
    )

    assumptions = analysis.get(
        "assumptions",
        []
    )

    market_constraints = analysis.get(
        "market_constraints",
        []
    )

    market_risks = analysis.get(
        "market_risks",
        []
    )


    # ========================================================
    # SAFETY NORMALIZATION
    # ========================================================

    if not isinstance(target_customers, list):
        target_customers = [str(target_customers)]

    if not isinstance(competition, list):
        competition = [str(competition)]

    if not isinstance(market_opportunities, list):
        market_opportunities = [str(market_opportunities)]

    if not isinstance(missing_information, list):
        missing_information = [str(missing_information)]

    if not isinstance(assumptions, list):
        assumptions = [str(assumptions)]

    if not isinstance(market_constraints, list):
        market_constraints = [str(market_constraints)]

    if not isinstance(market_risks, list):
        market_risks = [str(market_risks)]


    # ========================================================
    # LIMIT LIST SIZE
    # ========================================================

    target_customers = target_customers[:5]

    competition = competition[:5]

    market_opportunities = market_opportunities[:5]

    missing_information = missing_information[:5]

    assumptions = assumptions[:5]

    market_constraints = market_constraints[:5]

    market_risks = market_risks[:5]


    # ========================================================
    # STRING FIELDS
    # ========================================================

    market_overview = analysis.get(
        "market_overview",
        ""
    )

    market_demand = analysis.get(
        "market_demand",
        ""
    )

    business_model = analysis.get(
        "business_model",
        ""
    )

    growth_potential = analysis.get(
        "growth_potential",
        ""
    )

    recommendation = analysis.get(
        "recommendation",
        ""
    )

    confidence = analysis.get(
        "confidence",
        ""
    )


    # ========================================================
    # FINAL MARKET RESULT
    # ========================================================

    return {

        "domain": "market",

        # ----------------------------------------------------
        # User-provided market information
        # ----------------------------------------------------

        "user_provided_data": {

            "target_customers":
                target_customers,

            "market_demand":
                market_demand,

            "competition":
                competition,

            "business_model":
                business_model,

            "market_constraints":
                market_constraints
        },

        # ----------------------------------------------------
        # Market analysis
        # ----------------------------------------------------

        "market_overview":
            market_overview,

        "target_customers":
            target_customers,

        "market_demand":
            market_demand,

        "competition":
            competition,

        "business_model":
            business_model,

        "market_opportunities":
            market_opportunities,

        "missing_information":
            missing_information,

        "assumptions":
            assumptions,

        "market_constraints":
            market_constraints,

        "market_risks":
            market_risks,

        "growth_potential":
            growth_potential,

        "recommendation":
            recommendation,

        "confidence":
            confidence
    }