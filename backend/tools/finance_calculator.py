def calculate_profit(revenue: float, operating_cost: float) -> float:
    """
    Calculate annual operating profit.
    """
    return revenue - operating_cost


def calculate_profit_margin(
    profit: float,
    revenue: float
) -> float:
    """
    Calculate profit margin percentage.
    """

    if revenue <= 0:
        raise ValueError("Revenue must be greater than zero.")

    return (profit / revenue) * 100


def calculate_roi(
    profit: float,
    investment: float
) -> float:
    """
    Calculate simple ROI percentage.
    """

    if investment <= 0:
        raise ValueError("Investment must be greater than zero.")

    return (profit / investment) * 100


def calculate_payback_period(investment, annual_profit):
    """
    Calculate the simple payback period in years.

    Returns None if the project does not generate
    a positive annual profit.
    """

    if investment <= 0:
        raise ValueError("Investment must be greater than zero.")

    if annual_profit <= 0:
        return None

    return investment / annual_profit