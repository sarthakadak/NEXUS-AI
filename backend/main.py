from orchestrator import run_all_agents


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
    print(finance["financial_overview"])

    print("\nFinancial Risks:")
    for risk in finance["financial_risks"]:
        print(f"- {risk}")

    print("\nRecommendation:")
    print(finance["recommendation"])

    print("\n\nTECHNICAL ANALYSIS")
    print("------------------")
    print(technical["technical_overview"])

    print("\nTechnical Complexity:")
    print(technical["technical_complexity"])

    print("\nTechnical Risks:")
    for risk in technical["technical_risks"]:
        print(f"- {risk}")

    print("\nRecommendation:")
    print(technical["recommendation"])

    print("\n\nMARKET ANALYSIS")
    print("----------------")
    print(market["market_overview"])

    print("\nMarket Opportunities:")
    for opportunity in market["market_opportunities"]:
        print(f"- {opportunity}")

    print("\nMarket Risks:")
    for risk in market["market_risks"]:
        print(f"- {risk}")

    print("\nRecommendation:")
    print(market["recommendation"])

    print("\n\n========================================")
    print("             FINAL DECISION")
    print("========================================")

    print("\nOverall Feasibility:")
    print(decision["overall_feasibility"])

    print("\nDecision:")
    print(decision["decision"])

    print("\nKey Strengths:")
    for strength in decision["key_strengths"]:
        print(f"- {strength}")

    print("\nKey Concerns:")
    for concern in decision["key_concerns"]:
        print(f"- {concern}")

    print("\nCritical Missing Information:")
    for item in decision["critical_missing_information"]:
        print(f"- {item}")

    print("\nFinal Recommendation:")
    print(decision["final_recommendation"])

    print("\nConfidence:")
    print(decision["confidence"])

    print("\n========================================")
    print("          END OF REPORT")
    print("========================================\n")


if __name__ == "__main__":
    main()