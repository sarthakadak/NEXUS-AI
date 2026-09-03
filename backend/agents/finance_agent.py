import json
import re

from agents.llm_client import call_llm_json

from tools.finance_calculator import (
    calculate_profit,
    calculate_profit_margin,
    calculate_roi,
    calculate_payback_period
)


FINANCE_SYSTEM_PROMPT = """
You are the Finance Agent in a multi-agent AI system.

Analyze ONLY the financial aspects of the user's problem.

Identify:
- explicit financial facts
- pricing/revenue information
- customers/users/units/revenue-generating quantities
- upfront/investment costs
- annual operating expenses
- profitability
- financial risks
- financial recommendation
- confidence

Rules:
1. Never invent financial facts.
2. Distinguish facts, assumptions, and Python calculations.
3. Never perform arithmetic yourself; Python performs calculations.
4. Recognize amounts written as lakh, crore, million, thousand, or with currency symbols.
5. A stated TOTAL/DIRECT initial investment is authoritative.
6. A standalone upfront development/software/hardware/equipment/setup/licensing/
   integration/initial-marketing cost is an upfront capital component unless it
   is explicitly part of an already-stated total.
7. A stated TOTAL/DIRECT annual revenue must be captured directly.
8. Revenue quantity and capital/deployment quantity are not automatically the same.
9. A stated combined annual operating expense is sufficient; do not require
   every component separately.
10. Explicit no revenue/free/revenue zero means revenue = 0.
11. Return ONLY valid JSON. No Markdown.
"""


def _safe_number(value):
    """Convert common numeric and financial strings to a number."""
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return value

    try:
        text = str(value).strip().lower()
        if not text:
            return None

        text = (
            text.replace(",", "")
            .replace("₹", "")
            .replace("$", "")
            .replace("€", "")
            .replace("£", "")
        )

        scale = 1.0

        if re.search(r"\b(crore|crores|cr)\b", text):
            scale = 10_000_000.0
        elif re.search(r"\b(lakh|lakhs|lac|lacs)\b", text):
            scale = 100_000.0
        elif re.search(r"\b(million|mn)\b", text):
            scale = 1_000_000.0
        elif re.search(r"\b(thousand|k)\b", text):
            scale = 1_000.0

        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return None

        number = float(match.group(0)) * scale
        return int(number) if number.is_integer() else number

    except (ValueError, TypeError):
        return None


def _extract_direct_annual_revenue_from_text(problem):
    """Conservative fallback for explicitly stated total annual revenue."""
    patterns = [
        r"(?:expected|projected|estimated|anticipated)?\s*annual\s+revenue"
        r"\s*(?:is|of|will\s+be|=|:)\s*(?:₹|\$|€|£)?\s*"
        r"([\d,.]+)\s*(lakh|lakhs|lac|lacs|crore|crores|cr|million|mn|thousand|k)?",

        r"(?:expected|projected|estimated|anticipated)?\s*yearly\s+revenue"
        r"\s*(?:is|of|will\s+be|=|:)\s*(?:₹|\$|€|£)?\s*"
        r"([\d,.]+)\s*(lakh|lakhs|lac|lacs|crore|crores|cr|million|mn|thousand|k)?",

        r"revenue\s+of\s*(?:₹|\$|€|£)?\s*"
        r"([\d,.]+)\s*(lakh|lakhs|lac|lacs|crore|crores|cr|million|mn|thousand|k)?"
        r"\s*(?:per\s+year|annually|a\s+year)"
    ]

    for pattern in patterns:
        match = re.search(pattern, problem, flags=re.IGNORECASE)
        if match:
            value = _safe_number(
                f"{match.group(1)} {match.group(2) or ''}"
            )
            if value is not None:
                return value

    return None


def _extract_upfront_cost_fallbacks(problem):
    """Conservative fallback for obvious standalone upfront costs."""
    patterns = [
        (
            r"(?:initial\s+)?development\s+cost"
            r"\s*(?:is|of|=|:)\s*(?:₹|\$|€|£)?\s*"
            r"([\d,.]+)\s*(lakh|lakhs|lac|lacs|crore|crores|cr|million|mn|thousand|k)?",
            "Development cost",
        ),
        (
            r"software\s+(?:development\s+)?cost"
            r"\s*(?:is|of|=|:)\s*(?:₹|\$|€|£)?\s*"
            r"([\d,.]+)\s*(lakh|lakhs|lac|lacs|crore|crores|cr|million|mn|thousand|k)?",
            "Software development cost",
        ),
        (
            r"(?:initial\s+)?setup\s+cost"
            r"\s*(?:is|of|=|:)\s*(?:₹|\$|€|£)?\s*"
            r"([\d,.]+)\s*(lakh|lakhs|lac|lacs|crore|crores|cr|million|mn|thousand|k)?",
            "Setup cost",
        ),
    ]

    results = []
    for pattern, description in patterns:
        match = re.search(pattern, problem, flags=re.IGNORECASE)
        if match:
            value = _safe_number(
                f"{match.group(1)} {match.group(2) or ''}"
            )
            if value is not None:
                results.append({
                    "description": description,
                    "amount": value
                })
    return results


def analyze_finance(problem: str) -> dict:

    extraction_prompt = f"""
Extract ONLY financial facts explicitly provided by the user.

USER PROBLEM:
{problem}

Return ONLY valid JSON using EXACTLY this structure:

{{
    "number_of_units": null,
    "revenue_units": null,
    "monthly_price_per_unit": null,
    "annual_price_per_unit": null,

    "cost_per_unit": null,
    "installation_cost_per_unit": null,

    "initial_investment": null,
    "additional_initial_costs": [],
    "direct_annual_revenue": null,

    "annual_operating_cost": null,
    "annual_electricity_cost": null,
    "annual_maintenance_cost": null,

    "explicit_no_revenue": false
}}

STRICT RULES:

1. Extract ONLY facts explicitly provided by the user.
2. Never invent missing values.
3. Never perform arithmetic.
4. number_of_units = quantity associated with capital/deployment costs.
5. revenue_units = quantity explicitly associated with revenue.
6. NEVER assume number_of_units and revenue_units are the same.
7. monthly_price_per_unit = explicit monthly revenue price per revenue unit.
8. annual_price_per_unit = explicit annual revenue price per revenue unit.
9. Recognize annual pricing phrases including:
   "per year", "annually", "yearly", "₹X/year/customer",
   "each customer generates ₹X per year", "each user contributes ₹X annually".
10. direct_annual_revenue = explicitly stated TOTAL annual/yearly revenue.
11. Examples:
    "expected annual revenue is ₹15 lakh" -> 1500000
    "annual revenue is ₹8 lakh" -> 800000
    "projected yearly revenue is ₹20 lakh" -> 2000000
12. If direct annual revenue is stated, use direct_annual_revenue.
    Do not require customers or price-per-unit.
13. If revenue is quantity × price, use revenue_units and the relevant price.
14. initial_investment is ONLY an explicitly stated TOTAL/DIRECT initial,
    capital, startup, or equivalent aggregate investment.
15. Standalone upfront development/software/hardware/equipment/setup/licensing/
    integration/initial-marketing costs go into additional_initial_costs.
16. Each additional_initial_costs item must be:
    {{"description": "short description", "amount": number}}
17. If total investment and components are both stated, total investment wins.
18. Do not duplicate a total investment as component costs.
19. annual_operating_cost = total annual operating expense when explicitly
    stated as a combined amount.
20. If electricity and maintenance are separately stated, extract separately.
21. Do not split a combined annual expense into components.
22. Explicit "no revenue", "free", "revenue is zero", or "charging is free"
    means explicit_no_revenue = true.
23. Convert lakh/crore/million/thousand to plain numeric values.
24. Numbers contain no currency symbols or commas.
25. Return complete valid JSON.
26. No Markdown.
"""

    financial_data = call_llm_json(
        "finance",
        FINANCE_SYSTEM_PROMPT,
        extraction_prompt,
        max_tokens=1200
    )

    if not isinstance(financial_data, dict):
        financial_data = {}

    number_of_units = _safe_number(financial_data.get("number_of_units"))
    revenue_units = _safe_number(financial_data.get("revenue_units"))
    monthly_price_per_unit = _safe_number(
        financial_data.get("monthly_price_per_unit")
    )
    annual_price_per_unit = _safe_number(
        financial_data.get("annual_price_per_unit")
    )

    cost_per_unit = _safe_number(financial_data.get("cost_per_unit"))
    installation_cost_per_unit = _safe_number(
        financial_data.get("installation_cost_per_unit")
    )

    investment = _safe_number(financial_data.get("initial_investment"))

    direct_annual_revenue = _safe_number(
        financial_data.get("direct_annual_revenue")
    )

    additional_initial_costs = financial_data.get(
        "additional_initial_costs", []
    )
    if not isinstance(additional_initial_costs, list):
        additional_initial_costs = []

    normalized_additional_initial_costs = []

    for item in additional_initial_costs:
        if not isinstance(item, dict):
            continue

        amount = _safe_number(item.get("amount"))
        if amount is None:
            continue

        normalized_additional_initial_costs.append({
            "description": str(
                item.get("description", "Additional initial cost")
            ),
            "amount": amount
        })

    # Conservative fallback only when the LLM missed an obvious direct value.
    if direct_annual_revenue is None:
        direct_annual_revenue = _extract_direct_annual_revenue_from_text(
            problem
        )

    # Conservative fallback for standalone development/setup costs.
    fallback_costs = _extract_upfront_cost_fallbacks(problem)

    existing_amounts = {
        item["amount"]
        for item in normalized_additional_initial_costs
    }

    for item in fallback_costs:
        if item["amount"] not in existing_amounts:
            normalized_additional_initial_costs.append(item)
            existing_amounts.add(item["amount"])

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
        financial_data.get("explicit_no_revenue", False)
    )

    # ========================================================
    # INITIAL INVESTMENT
    # ========================================================

    unit_investment = None

    if number_of_units is not None:
        per_unit_cost = 0
        has_per_unit_cost = False

        if cost_per_unit is not None:
            per_unit_cost += cost_per_unit
            has_per_unit_cost = True

        if installation_cost_per_unit is not None:
            per_unit_cost += installation_cost_per_unit
            has_per_unit_cost = True

        if has_per_unit_cost:
            unit_investment = number_of_units * per_unit_cost

    additional_investment = sum(
        item["amount"]
        for item in normalized_additional_initial_costs
    )

    if investment is None:
        component_investment = 0
        has_component_investment = False

        if unit_investment is not None:
            component_investment += unit_investment
            has_component_investment = True

        if additional_investment > 0:
            component_investment += additional_investment
            has_component_investment = True

        if has_component_investment:
            investment = component_investment

    # ========================================================
    # ANNUAL OPERATING COST
    # ========================================================

    operating_cost = None

    if annual_operating_cost is not None:
        operating_cost = annual_operating_cost
    elif electricity_cost is not None and maintenance_cost is not None:
        operating_cost = electricity_cost + maintenance_cost

    # ========================================================
    # ANNUAL REVENUE
    # ========================================================

    revenue = None

    if explicit_no_revenue:
        revenue = 0
    elif direct_annual_revenue is not None:
        revenue = direct_annual_revenue
    else:
        revenue_quantity = (
            revenue_units
            if revenue_units is not None
            else number_of_units
        )

        if (
            revenue_quantity is not None
            and annual_price_per_unit is not None
        ):
            revenue = revenue_quantity * annual_price_per_unit

        elif (
            revenue_quantity is not None
            and monthly_price_per_unit is not None
        ):
            revenue = revenue_quantity * monthly_price_per_unit * 12

    # ========================================================
    # FINANCIAL METRICS
    # ========================================================

    calculated = {
        "initial_investment": (
            round(investment, 2) if investment is not None else None
        ),
        "unit_based_initial_investment": (
            round(unit_investment, 2)
            if unit_investment is not None
            else None
        ),
        "additional_initial_investment": round(
            additional_investment, 2
        ),
        "annual_revenue": (
            round(revenue, 2) if revenue is not None else None
        ),
        "annual_operating_expenses": (
            round(operating_cost, 2)
            if operating_cost is not None
            else None
        ),
        "annual_profit": None,
        "profit_margin_percent": None,
        "roi_percent": None,
        "payback_period_years": None
    }

    if revenue is not None and operating_cost is not None:
        profit = calculate_profit(revenue, operating_cost)
        calculated["annual_profit"] = round(profit, 2)

        if revenue > 0:
            calculated["profit_margin_percent"] = round(
                calculate_profit_margin(profit, revenue),
                2
            )

        if investment is not None and investment > 0:
            calculated["roi_percent"] = round(
                calculate_roi(profit, investment),
                2
            )

            payback = calculate_payback_period(
                investment,
                profit
            )

            if payback is not None:
                calculated["payback_period_years"] = round(
                    payback, 2
                )

    # ========================================================
    # CALCULATION BREAKDOWN
    # ========================================================

    calculation_breakdown = {}

    if investment is not None:
        direct_total = _safe_number(
            financial_data.get("initial_investment")
        )

        investment_parts = []

        if unit_investment is not None:
            unit_components = []

            if cost_per_unit is not None:
                unit_components.append(str(cost_per_unit))

            if installation_cost_per_unit is not None:
                unit_components.append(
                    str(installation_cost_per_unit)
                )

            investment_parts.append(
                f"{number_of_units} × "
                f"({' + '.join(unit_components)}) = "
                f"{unit_investment}"
            )

        for item in normalized_additional_initial_costs:
            investment_parts.append(
                f"{item['description']} = {item['amount']}"
            )

        if direct_total is not None:
            calculation_breakdown["initial_investment"] = (
                f"Directly stated total = {investment}"
            )
        elif investment_parts:
            calculation_breakdown["initial_investment"] = (
                " + ".join(investment_parts)
                + f" = {investment}"
            )

    # ALWAYS initialize this variable before using it.
    revenue_quantity = (
        revenue_units
        if revenue_units is not None
        else number_of_units
    )

    if direct_annual_revenue is not None and revenue is not None:
        calculation_breakdown["annual_revenue"] = (
            f"Directly stated annual revenue = {direct_annual_revenue}"
        )
    elif (
        revenue_quantity is not None
        and monthly_price_per_unit is not None
        and revenue is not None
    ):
        calculation_breakdown["annual_revenue"] = (
            f"{revenue_quantity} × "
            f"{monthly_price_per_unit} × 12 = {revenue}"
        )
    elif (
        revenue_quantity is not None
        and annual_price_per_unit is not None
        and revenue is not None
    ):
        calculation_breakdown["annual_revenue"] = (
            f"{revenue_quantity} × "
            f"{annual_price_per_unit} = {revenue}"
        )

    if (
        revenue is not None
        and operating_cost is not None
        and calculated["annual_profit"] is not None
    ):
        calculation_breakdown["annual_profit"] = (
            f"{revenue} - {operating_cost} = "
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
    # QUALITATIVE ANALYSIS
    # ========================================================

    calculation_input = {
        "initial_investment": investment,
        "unit_based_initial_investment": unit_investment,
        "additional_initial_costs": normalized_additional_initial_costs,
        "additional_initial_investment": additional_investment,
        "revenue_units": revenue_units,
        "direct_annual_revenue": direct_annual_revenue,
        "annual_revenue": revenue,
        "annual_operating_expenses": operating_cost,
        "annual_electricity_cost": electricity_cost,
        "annual_maintenance_cost": maintenance_cost
    }

    analysis_prompt = f"""
Analyze ONLY the financial aspects of this problem.

USER PROBLEM:
{problem}

RAW USER-PROVIDED FINANCIAL DATA:
{json.dumps(financial_data)}

NORMALIZED FINANCIAL DATA:
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

RULES:
1. Do not invent financial facts.
2. Do not perform new calculations.
3. Use Python-calculated values exactly as provided.
4. Do not list calculated values as missing.
5. If direct_annual_revenue or annual_revenue exists, annual revenue is known.
6. If initial_investment exists, initial investment is known.
7. If aggregate annual operating expenses exist, do not list their individual
   components as missing merely because they are not itemized.
8. If annual profit is negative, state that the project operates at a loss.
9. If annual profit is positive, state that the project generates operating profit.
10. If revenue is zero, recognize that there is no revenue stream.
11. Distinguish assumptions from explicit facts.
12. Do not perform technical or market analysis.
13. Do not make the final overall decision.
14. Maximum 5 items per list.
15. Keep list items concise.
16. Keep each string under 30 words.
17. Return complete valid JSON.
18. No Markdown.
"""

    qualitative_analysis = call_llm_json(
        "finance",
        FINANCE_SYSTEM_PROMPT,
        analysis_prompt,
        max_tokens=1600
    )

    if not isinstance(qualitative_analysis, dict):
        qualitative_analysis = {}

    return {
        "domain": "finance",
        "user_provided_data": financial_data,
        "calculated_metrics": calculated,
        "calculation_breakdown": calculation_breakdown,
        "financial_overview": qualitative_analysis.get(
            "financial_overview", ""
        ),
        "missing_information": qualitative_analysis.get(
            "missing_information", []
        ),
        "assumptions": qualitative_analysis.get(
            "assumptions", []
        ),
        "financial_risks": qualitative_analysis.get(
            "financial_risks", []
        ),
        "recommendation": qualitative_analysis.get(
            "recommendation", ""
        ),
        "confidence": qualitative_analysis.get(
            "confidence", ""
        )
    }
