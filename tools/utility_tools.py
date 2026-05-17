"""
tools/utility_tools.py
-----------------------
PURPOSE: General-purpose utility tools that are not domain-specific.
         These demonstrate additional tool patterns:
         - Tools that call external sources (simulated here)
         - Tools with multiple parameters
         - Tools that do computation/formatting

         In a real project, you'd add tools here for:
         - Web search (via Tavily, SerpAPI, etc.)
         - Calendar lookups
         - Email/Slack sending
         - Database queries
"""

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_date_and_time() -> str:
    """
    Get the current date and time.

    Use this tool when:
    - The user's question involves "today", "this week", "this month"
    - You need to calculate time-sensitive values like days until quarter-end
    - You need to contextualize performance metrics relative to the current date

    Returns:
        Current date and time as a formatted string with timezone info.
    """
    now = datetime.now()
    return (
        f"Current Date & Time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}\n"
        f"Day of Year: {now.timetuple().tm_yday}/365\n"
        f"Year Progress: {(now.timetuple().tm_yday / 365 * 100):.1f}%\n"
        f"Quarter: Q{(now.month - 1) // 3 + 1}"
    )


@tool
def calculate_rep_ranking(metric: str) -> str:
    """
    Rank all sales reps by a given performance metric.

    Use this tool when:
    - The user asks "who is the top performer?"
    - The user wants to compare reps side-by-side
    - You need a leaderboard or ranking

    Args:
        metric: The metric to rank by. Valid options:
                - "quota_attainment" — rank by % of quota achieved
                - "ytd_sales"        — rank by absolute YTD sales dollars
                - "tenure"           — rank by years of experience

    Returns:
        A ranked list of reps with their metric values.
    """
    # Import here to avoid circular imports between tool files
    from tools.rep_tools import REPS_DB

    valid_metrics = ["quota_attainment", "ytd_sales", "tenure"]
    if metric not in valid_metrics:
        return (
            f"Invalid metric '{metric}'. "
            f"Valid options: {', '.join(valid_metrics)}"
        )

    if metric == "quota_attainment":
        ranked = sorted(
            REPS_DB.items(),
            key=lambda x: x[1]["ytd_sales_usd"] / x[1]["quota_usd"],
            reverse=True,
        )
        lines = ["🏆 Ranking by Quota Attainment:\n"]
        for rank, (rep_id, rep) in enumerate(ranked, start=1):
            pct = (rep["ytd_sales_usd"] / rep["quota_usd"]) * 100
            lines.append(f"  #{rank} {rep['name']} ({rep_id}): {pct:.1f}%")

    elif metric == "ytd_sales":
        ranked = sorted(
            REPS_DB.items(),
            key=lambda x: x[1]["ytd_sales_usd"],
            reverse=True,
        )
        lines = ["💰 Ranking by YTD Sales:\n"]
        for rank, (rep_id, rep) in enumerate(ranked, start=1):
            lines.append(
                f"  #{rank} {rep['name']} ({rep_id}): "
                f"${rep['ytd_sales_usd']:,}"
            )

    elif metric == "tenure":
        ranked = sorted(
            REPS_DB.items(),
            key=lambda x: x[1]["tenure_years"],
            reverse=True,
        )
        lines = ["📅 Ranking by Tenure:\n"]
        for rank, (rep_id, rep) in enumerate(ranked, start=1):
            lines.append(
                f"  #{rank} {rep['name']} ({rep_id}): "
                f"{rep['tenure_years']} years"
            )

    return "\n".join(lines)


@tool
def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format a numeric amount as a currency string.

    Use this tool when you need to present monetary values in a clean,
    human-readable format for reports or summaries.

    Args:
        amount: The numeric amount to format.
        currency: Currency code (default: 'USD'). Supported: USD, EUR, GBP.

    Returns:
        Formatted currency string (e.g., '$1,234,567.00').
    """
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency.upper(), currency + " ")
    return f"{symbol}{amount:,.2f}"
