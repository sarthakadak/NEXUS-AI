from agents.finance_agent import analyze_finance
from agents.technical_agent import analyze_technical
from agents.market_agent import analyze_market
from agents.decision_agent import make_final_decision


def run_all_agents(problem: str) -> dict:
    """
    Run all domain agents and then send their
    results to the Final Decision Agent.
    """

    # Step 1: Run Finance Agent
    finance_result = analyze_finance(problem)

    # Step 2: Run Technical Agent
    technical_result = analyze_technical(problem)

    # Step 3: Run Market Agent
    market_result = analyze_market(problem)

    # Step 4: Final Decision Agent
    final_decision = make_final_decision(
        finance_result,
        technical_result,
        market_result
    )

    # Step 5: Return complete MAS result
    return {
        "problem": problem,

        "finance_analysis": finance_result,

        "technical_analysis": technical_result,

        "market_analysis": market_result,

        "final_decision": final_decision
    }