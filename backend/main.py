from orchestrator import run_all_agents


def _print_list(title, items):
    print(f"\n{title}:")
    if items:
        for item in items:
            print(f"- {item}")
    else:
        print("- None reported")


def main():

    print("\n========================================")
    print("       MULTI-AGENT AI SYSTEM")
    print("========================================\n")

    problem = input("Enter your problem statement:\n> ")

    if not problem.strip():
        print("\nERROR: Problem statement cannot be empty.")
        return

    print("\nAnalyzing problem using multiple AI agents...\n")

    result = run_all_agents(problem)

    finance = result["finance_analysis"]
    technical = result["technical_analysis"]
    market = result["market_analysis"]
    decision = result["final_decision"]

    print("\n========================================")
    print("             FINAL REPORT")
    print("========================================")

    print("\nPROBLEM")
    print("-------")
    print(problem)

    print("\n\nFINANCE ANALYSIS")
    print("----------------")
    print(finance.get("financial_overview", ""))

    _print_list("Financial Risks", finance.get("financial_risks", []))

    print("\nRecommendation:")
    print(finance.get("recommendation", ""))

    # Show deterministic financial metrics when available.
    metrics = finance.get("calculated_metrics", {})
    if metrics:
        print("\nCalculated Financial Metrics:")
        metric_labels = {
            "annual_revenue": "Annual Revenue",
            "annual_operating_expenses": "Annual Operating Expenses",
            "annual_profit": "Annual Profit",
            "profit_margin_percent": "Profit Margin",
            "roi_percent": "ROI",
            "payback_period_years": "Payback Period",
        }

        for key, label in metric_labels.items():
            value = metrics.get(key)
            if value is not None:
                suffix = "%" if key in {"profit_margin_percent", "roi_percent"} else ""
                if key == "payback_period_years":
                    suffix = " years"
                print(f"- {label}: {value}{suffix}")

    print("\n\nTECHNICAL ANALYSIS")
    print("------------------")
    print(technical.get("technical_overview", ""))

    print("\nTechnical Complexity:")
    print(technical.get("technical_complexity", ""))

    _print_list("Technical Risks", technical.get("technical_risks", []))

    print("\nRecommendation:")
    print(technical.get("recommendation", ""))

    print("\n\nMARKET ANALYSIS")
    print("----------------")
    print(market.get("market_overview", ""))

    _print_list("Target Customers", market.get("target_customers", []))

    print("\nMarket Demand:")
    print(market.get("market_demand", ""))

    _print_list("Competition", market.get("competition", []))

    print("\nBusiness Model:")
    print(market.get("business_model", ""))

    _print_list("Market Opportunities", market.get("market_opportunities", []))

    _print_list("Missing Market Information", market.get("missing_information", []))

    _print_list("Market Assumptions", market.get("assumptions", []))

    _print_list("Market Constraints", market.get("market_constraints", []))

    _print_list("Market Risks", market.get("market_risks", []))

    print("\nGrowth Potential:")
    print(market.get("growth_potential", ""))

    print("\nRecommendation:")
    print(market.get("recommendation", ""))

    print("\nMarket Confidence:")
    print(market.get("confidence", ""))

    print("\n\n========================================")
    print("             FINAL DECISION")
    print("========================================")

    print("\nOverall Feasibility:")
    print(decision.get("overall_feasibility", ""))

    print("\nDecision:")
    print(decision.get("decision", ""))

    _print_list("Key Strengths", decision.get("key_strengths", []))

    _print_list("Key Concerns", decision.get("key_concerns", []))

    _print_list(
        "Critical Missing Information",
        decision.get("critical_missing_information", [])
    )

    _print_list("Agent Agreement", decision.get("agent_agreement", []))

    _print_list("Agent Conflicts", decision.get("agent_conflicts", []))

    print("\nFinal Recommendation:")
    print(decision.get("final_recommendation", ""))

    print("\nConfidence:")
    print(decision.get("confidence", ""))

    print("\n========================================")
    print("          END OF REPORT")
    print("========================================\n")


if __name__ == "__main__":
    main()
