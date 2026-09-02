import json

from agents.llm_client import call_llm_json

from tools.finance_calculator import (
    calculate_profit,
    calculate_profit_margin,
    calculate_roi,
    calculate_payback_period
)


# ============================================================
# FINANCE AGENT SYSTEM PROMPT
# ============================================================

FINANCE_SYSTEM_PROMPT = """
You are the Finance Agent in a multi-agent AI system.

Your job is to analyze ONLY the financial aspects of a problem.

You must identify:

- User-provided financial data
- Pricing information
- Number of customers or units
- Costs
- Revenue
- Profitability
- ROI
- Payback period
- Financial risks
- Financial recommendation
- Confidence level

IMPORTANT RULES:

1. Never invent user-provided financial data.
2. Clearly distinguish facts, assumptions, estimates and calculations.
3. If information is missing, report it.
4. Explicit statements such as "no revenue" mean revenue = 0.
5. Numerical calculations must be performed by Python, not by the LLM.
6. Do not perform technical or market analysis.
7. Do not make the final overall decision.
8. Return ONLY valid JSON.
9. Do not use Markdown.
"""


# ============================================================
# SAFE NUMBER HELPER
# ============================================================

def _safe_number(value):
    """
    Convert a value to a number when possible.
    Return None if the value is missing or invalid.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return value

    try:
        value = str(value)

        # Remove common formatting
        value = (
            value
            .replace(",", "")
            .replace("₹", "")
            .replace("$", "")
            .replace("€", "")
            .replace("£", "")
            .strip()
        )

        if value == "":
            return None

        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except (ValueError, TypeError):
        return None


# ============================================================
# FINANCE ANALYSIS
# ============================================================

def analyze_finance(problem: str) -> dict:

    # ========================================================
    # STEP 1: EXTRACT RAW FINANCIAL FACTS
    # ========================================================

    extraction_prompt = f"""
Extract ONLY financial facts explicitly provided by the user.

USER PROBLEM:

{problem}

Return ONLY valid JSON using EXACTLY this structure:

{{
    "number_of_units": null,
    "monthly_price_per_unit": null,
    "annual_price_per_unit": null,

    "cost_per_unit": null,
    "installation_cost_per_unit": null,

    "initial_investment": null,

    "annual_operating_cost": null,
    "annual_electricity_cost": null,
    "annual_maintenance_cost": null,

    "explicit_no_revenue": false
}}

STRICT RULES:

1. Extract only information explicitly provided by the user.
2. Do NOT invent missing values.
3. Do NOT perform calculations.
4. Do NOT calculate annual revenue.
5. Do NOT calculate total investment.
6. Do NOT calculate total operating expenses.
7. Do NOT calculate profit.
8. Do NOT calculate ROI.
9. Do NOT calculate payback period.
10. "number_of_units" means explicitly stated number of customers,
    restaurants, systems, stations, subscriptions, or similar units.
11. "monthly_price_per_unit" means an explicitly stated monthly
    price charged per customer or unit.
12. "annual_price_per_unit" means an explicitly stated annual
    price charged per customer or unit.
13. If the user explicitly says there is no revenue,
    charging is free, or revenue is zero, set
    "explicit_no_revenue" to true.
14. If a value is not provided, use null.
15. Numbers must contain no currency symbols or commas.
16. Return complete valid JSON.
17. No Markdown.
"""

    financial_data = call_llm_json(
        "finance",
        FINANCE_SYSTEM_PROMPT,
        extraction_prompt,
        max_tokens=900
    )


    # ========================================================
    # STEP 1.1: NORMALIZE RAW VALUES
    # ========================================================

    number_of_units = _safe_number(
        financial_data.get("number_of_units")
    )

    monthly_price_per_unit = _safe_number(
        financial_data.get("monthly_price_per_unit")
    )

    annual_price_per_unit = _safe_number(
        financial_data.get("annual_price_per_unit")
    )

    cost_per_unit = _safe_number(
        financial_data.get("cost_per_unit")
    )

    installation_cost_per_unit = _safe_number(
        financial_data.get("installation_cost_per_unit")
    )

    investment = _safe_number(
        financial_data.get("initial_investment")
    )

    annual_operating_cost = _safe_number(
        financial_data.get("annual_operating_cost")
    )

    electricity_cost = _safe_number(
        financial_data.get("annual_electricity_cost")
    )

    maintenance_cost = _safe_number(
        financial_data.get("annual_maintenance_cost")
    )

    explicit_no_revenue = bool(
        financial_data.get(
            "explicit_no_revenue",
            False
        )
    )


    # ========================================================
    # STEP 2: DETERMINISTIC PYTHON CALCULATIONS
    # ========================================================

    # --------------------------------------------------------
    # INITIAL INVESTMENT
    # --------------------------------------------------------

    if investment is None:

        if (
            number_of_units is not None
            and cost_per_unit is not None
            and installation_cost_per_unit is not None
        ):

            investment = (
                number_of_units
                * (
                    cost_per_unit
                    + installation_cost_per_unit
                )
            )


    # --------------------------------------------------------
    # ANNUAL OPERATING COST
    # --------------------------------------------------------

    operating_cost = None

    # Direct annual operating cost has priority.
    if annual_operating_cost is not None:

        operating_cost = annual_operating_cost

    # Otherwise calculate from explicitly provided components.
    elif (
        electricity_cost is not None
        and maintenance_cost is not None
    ):

        operating_cost = (
            electricity_cost
            + maintenance_cost
        )


    # --------------------------------------------------------
    # ANNUAL REVENUE
    # --------------------------------------------------------

    revenue = None

    # Explicit zero revenue has highest priority.
    if explicit_no_revenue:

        revenue = 0

    # Direct annual price × number of units.
    elif (
        number_of_units is not None
        and annual_price_per_unit is not None
    ):

        revenue = (
            number_of_units
            * annual_price_per_unit
        )

    # Monthly price × number of units × 12 months.
    elif (
        number_of_units is not None
        and monthly_price_per_unit is not None
    ):

        revenue = (
            number_of_units
            * monthly_price_per_unit
            * 12
        )


    # ========================================================
    # STEP 3: CALCULATE FINANCIAL METRICS
    # ========================================================

    calculated = {

        "annual_revenue": None,

        "annual_operating_expenses": None,

        "annual_profit": None,

        "profit_margin_percent": None,

        "roi_percent": None,

        "payback_period_years": None
    }


    # --------------------------------------------------------
    # Store calculated revenue
    # --------------------------------------------------------

    if revenue is not None:

        calculated["annual_revenue"] = round(
            revenue,
            2
        )


    # --------------------------------------------------------
    # Store operating expenses
    # --------------------------------------------------------

    if operating_cost is not None:

        calculated["annual_operating_expenses"] = round(
            operating_cost,
            2
        )


    # --------------------------------------------------------
    # PROFIT
    # --------------------------------------------------------

    if (
        revenue is not None
        and operating_cost is not None
    ):

        profit = calculate_profit(
            revenue,
            operating_cost
        )

        calculated["annual_profit"] = round(
            profit,
            2
        )


        # ----------------------------------------------------
        # PROFIT MARGIN
        # ----------------------------------------------------

        if revenue > 0:

            calculated["profit_margin_percent"] = round(
                calculate_profit_margin(
                    profit,
                    revenue
                ),
                2
            )


        # ----------------------------------------------------
        # ROI + PAYBACK
        # ----------------------------------------------------

        if (
            investment is not None
            and investment > 0
        ):

            calculated["roi_percent"] = round(
                calculate_roi(
                    profit,
                    investment
                ),
                2
            )

            payback = calculate_payback_period(
                investment,
                profit
            )

            if payback is not None:

                calculated["payback_period_years"] = round(
                    payback,
                    2
                )


    # ========================================================
    # STEP 4: CALCULATION BREAKDOWN
    # ========================================================

    calculation_breakdown = {}


    if (
        number_of_units is not None
        and monthly_price_per_unit is not None
        and revenue is not None
    ):

        calculation_breakdown["annual_revenue"] = (
            f"{number_of_units} × "
            f"{monthly_price_per_unit} × 12 = "
            f"{revenue}"
        )

    elif (
        number_of_units is not None
        and annual_price_per_unit is not None
        and revenue is not None
    ):

        calculation_breakdown["annual_revenue"] = (
            f"{number_of_units} × "
            f"{annual_price_per_unit} = "
            f"{revenue}"
        )


    if (
        revenue is not None
        and operating_cost is not None
        and calculated["annual_profit"] is not None
    ):

        calculation_breakdown["annual_profit"] = (
            f"{revenue} - "
            f"{operating_cost} = "
            f"{calculated['annual_profit']}"
        )


    if (
        calculated["annual_profit"] is not None
        and investment is not None
        and calculated["roi_percent"] is not None
    ):

        calculation_breakdown["roi"] = (
            f"{calculated['annual_profit']} / "
            f"{investment} × 100 = "
            f"{calculated['roi_percent']}%"
        )


    if (
        investment is not None
        and calculated["annual_profit"] is not None
        and calculated["payback_period_years"] is not None
    ):

        calculation_breakdown["payback_period"] = (
            f"{investment} / "
            f"{calculated['annual_profit']} = "
            f"{calculated['payback_period_years']} years"
        )


    # ========================================================
    # STEP 5: PREPARE DATA FOR QUALITATIVE ANALYSIS
    # ========================================================

    calculation_input = {

        "initial_investment": investment,

        "annual_revenue": revenue,

        "annual_operating_expenses": operating_cost,

        "annual_electricity_cost":
            electricity_cost,

        "annual_maintenance_cost":
            maintenance_cost
    }


    # ========================================================
    # STEP 6: QUALITATIVE FINANCIAL ANALYSIS
    # ========================================================

    analysis_prompt = f"""
Analyze ONLY the financial aspects of this problem.

USER PROBLEM:

{problem}

RAW USER-PROVIDED FINANCIAL DATA:

{json.dumps(financial_data)}

PYTHON-CALCULATED FINANCIAL INPUTS:

{json.dumps(calculation_input)}

PYTHON-CALCULATED METRICS:

{json.dumps(calculated)}

CALCULATION BREAKDOWN:

{json.dumps(calculation_breakdown)}

Return ONLY valid JSON using EXACTLY this structure:

{{
    "financial_overview": "",
    "missing_information": [],
    "assumptions": [],
    "financial_risks": [],
    "recommendation": "",
    "confidence": ""
}}

STRICT RULES:

1. Do NOT invent financial facts.
2. Do NOT perform new calculations.
3. Use Python-calculated values exactly as provided.
4. Do NOT list calculated values as missing information.
5. Only report genuinely missing financial information.
6. Clearly distinguish assumptions from facts.
7. If annual revenue is 0, recognize that there is no revenue stream.
8. If annual profit is negative, recognize that the project operates at a loss.
9. If annual profit is positive, recognize that the project generates operating profit.
10. Do not perform technical analysis.
11. Do not perform market analysis.
12. Do not make the final overall decision.
13. Maximum 5 items per list.
14. Keep each list item concise.
15. Keep each string under 30 words.
16. Return complete valid JSON.
17. No Markdown.
"""

    qualitative_analysis = call_llm_json(
        "finance",
        FINANCE_SYSTEM_PROMPT,
        analysis_prompt,
        max_tokens=1400
    )


    # ========================================================
    # STEP 7: FINAL FINANCE AGENT RESULT
    # ========================================================

    return {

        "domain": "finance",

        "user_provided_data": financial_data,

        "calculated_metrics": calculated,

        "calculation_breakdown":
            calculation_breakdown,

        "financial_overview":
            qualitative_analysis.get(
                "financial_overview",
                ""
            ),

        "missing_information":
            qualitative_analysis.get(
                "missing_information",
                []
            ),

        "assumptions":
            qualitative_analysis.get(
                "assumptions",
                []
            ),

        "financial_risks":
            qualitative_analysis.get(
                "financial_risks",
                []
            ),

        "recommendation":
            qualitative_analysis.get(
                "recommendation",
                ""
            ),

        "confidence":
            qualitative_analysis.get(
                "confidence",
                ""
            )
    }