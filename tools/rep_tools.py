"""
tools/rep_tools.py
------------------
PURPOSE: Domain-specific tools for "rep context" analysis.
         These tools simulate real-world integrations a sales intelligence
         agent would have — CRM lookups, performance calculators, etc.

         In a real system, these would make HTTP calls to Salesforce,
         HubSpot, or your internal APIs. Here they show the PATTERN:
         the agent decides which tool to call, calls it, observes the
         result, then reasons about what to do next.

IMPORTANT — Tool Docstrings:
         The LLM reads the docstring to decide WHEN to call each tool.
         Write them like a clear instruction for an intelligent assistant.
         Poor docstring → tool called at wrong time → bad agent behavior.
"""

import json
from datetime import datetime, timedelta
from langchain_core.tools import tool


# ─────────────────────────────────────────────────────────────────────────────
# Simulated in-memory "CRM database"
# In a real app, replace these dicts with API calls or DB queries
# ─────────────────────────────────────────────────────────────────────────────

REPS_DB = {
    "REP001": {
        "name": "Alice Johnson",
        "territory": "North-East",
        "product_line": "Enterprise SaaS",
        "quota_usd": 500000,
        "ytd_sales_usd": 312000,
        "tenure_years": 3.5,
        "manager": "Bob Martinez",
        "top_accounts": ["Acme Corp", "TechNova", "GlobalBank"],
        "specializations": ["cloud migration", "security compliance"],
    },
    "REP002": {
        "name": "Carlos Rivera",
        "territory": "South-West",
        "product_line": "Mid-Market SaaS",
        "quota_usd": 300000,
        "ytd_sales_usd": 289000,
        "tenure_years": 1.2,
        "manager": "Sarah Kim",
        "top_accounts": ["RetailPlus", "FastShip Co"],
        "specializations": ["e-commerce integrations", "logistics"],
    },
    "REP003": {
        "name": "Diana Patel",
        "territory": "West-Coast",
        "product_line": "Enterprise SaaS",
        "quota_usd": 600000,
        "ytd_sales_usd": 540000,
        "tenure_years": 6.0,
        "manager": "Bob Martinez",
        "top_accounts": ["SiliconStartups", "BioTech Inc", "MediaGroup"],
        "specializations": ["healthcare tech", "media & entertainment"],
    },
}

DEALS_DB = {
    "DEAL-2024-001": {
        "rep_id": "REP001",
        "account": "Acme Corp",
        "value_usd": 85000,
        "stage": "Negotiation",
        "close_date": "2024-06-30",
        "product": "Enterprise Plan",
    },
    "DEAL-2024-002": {
        "rep_id": "REP002",
        "account": "FastShip Co",
        "value_usd": 45000,
        "stage": "Proposal Sent",
        "close_date": "2024-07-15",
        "product": "Growth Plan",
    },
    "DEAL-2024-003": {
        "rep_id": "REP003",
        "account": "BioTech Inc",
        "value_usd": 120000,
        "stage": "Closed Won",
        "close_date": "2024-05-01",
        "product": "Enterprise Plan",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────────────────────────────────────

@tool
def lookup_rep_profile(rep_id: str) -> str:
    """
    Look up the full profile of a sales representative by their Rep ID.

    Use this tool when you need:
    - Basic information about a specific rep (name, territory, manager)
    - Their product line, specializations, or top accounts
    - Quota and year-to-date sales figures

    Args:
        rep_id: The unique identifier for the rep (e.g. 'REP001', 'REP002').
                If the user provides a name instead, try to infer the ID from
                context or ask the user to confirm.

    Returns:
        JSON string with the rep's full profile, or an error message if
        the rep ID is not found.
    """
    rep = REPS_DB.get(rep_id.upper())
    if not rep:
        available = ", ".join(REPS_DB.keys())
        return (
            f"Rep ID '{rep_id}' not found in the CRM. "
            f"Available rep IDs: {available}"
        )
    return json.dumps(rep, indent=2)


@tool
def calculate_quota_attainment(rep_id: str) -> str:
    """
    Calculate the quota attainment percentage for a sales representative.

    Use this tool when the user asks about:
    - How well a rep is performing against their quota
    - Quota attainment percentage or "% to quota"
    - Whether a rep is on track to hit their annual target
    - Performance comparisons between reps

    Quota attainment = (YTD Sales / Annual Quota) × 100

    Args:
        rep_id: The unique identifier for the rep (e.g. 'REP001').

    Returns:
        A string describing the rep's quota attainment, with a performance
        classification (e.g. On Track, Behind, Overachieving).
    """
    rep = REPS_DB.get(rep_id.upper())
    if not rep:
        return f"Rep ID '{rep_id}' not found."

    quota = rep["quota_usd"]
    ytd = rep["ytd_sales_usd"]

    # Calculate attainment as a percentage of annual quota
    attainment_pct = (ytd / quota) * 100

    # Determine where we are in the year (to contextualise the % achieved)
    now = datetime.now()
    year_progress_pct = (now.timetuple().tm_yday / 365) * 100

    # Classify performance relative to where they *should* be at this point
    if attainment_pct >= 100:
        status = "✅ Overachieving (quota fully met!)"
    elif attainment_pct >= year_progress_pct:
        status = "🟢 On Track (pacing above year-to-date target)"
    elif attainment_pct >= year_progress_pct * 0.85:
        status = "🟡 Slightly Behind (within 15% of expected pace)"
    else:
        status = "🔴 Behind (needs attention)"

    return (
        f"Rep: {rep['name']} ({rep_id.upper()})\n"
        f"Annual Quota: ${quota:,}\n"
        f"YTD Sales: ${ytd:,}\n"
        f"Quota Attainment: {attainment_pct:.1f}%\n"
        f"Year Progress: {year_progress_pct:.1f}%\n"
        f"Status: {status}"
    )


@tool
def get_rep_deals(rep_id: str) -> str:
    """
    Retrieve all active and recent deals (opportunities) for a specific
    sales representative.

    Use this tool when you need:
    - A list of open deals or opportunities for a rep
    - Deal values, stages, and expected close dates
    - Information about which accounts a rep is currently working

    Args:
        rep_id: The unique identifier for the rep (e.g. 'REP001').

    Returns:
        JSON string listing all deals associated with the rep, including
        account name, deal value, current stage, and close date.
        Returns a message if no deals are found for the rep.
    """
    rep_deals = {
        deal_id: deal
        for deal_id, deal in DEALS_DB.items()
        if deal["rep_id"].upper() == rep_id.upper()
    }

    if not rep_deals:
        return f"No deals found for Rep ID '{rep_id}'."

    # Add summary stats for convenience
    total_value = sum(d["value_usd"] for d in rep_deals.values())
    output = {
        "rep_id": rep_id.upper(),
        "deal_count": len(rep_deals),
        "total_pipeline_value_usd": total_value,
        "deals": rep_deals,
    }
    return json.dumps(output, indent=2)


@tool
def list_all_reps() -> str:
    """
    List all sales representatives in the system with brief summaries.

    Use this tool when:
    - The user asks "who are the reps?" or "show me all reps"
    - You need to find a rep by name (when you don't have their ID)
    - The user wants a general overview of the sales team

    Returns:
        A formatted string listing all rep IDs, names, territories, and
        product lines.
    """
    lines = ["Sales Representatives:\n"]
    for rep_id, rep in REPS_DB.items():
        lines.append(
            f"  {rep_id}: {rep['name']}"
            f" | Territory: {rep['territory']}"
            f" | Product: {rep['product_line']}"
        )
    return "\n".join(lines)


@tool
def summarize_rep_context(rep_id: str) -> str:
    """
    Generate a comprehensive context summary for a sales representative
    by combining their profile, quota attainment, and deal pipeline.

    Use this tool when:
    - The user asks for a "full picture" or "context" about a rep
    - You want to prepare a briefing before an important call or meeting
    - The user asks something broad like "tell me about REP001"

    This tool internally aggregates data from multiple sources (profile,
    performance, deals) into one cohesive summary — saving the agent
    from making three separate tool calls.

    Args:
        rep_id: The unique identifier for the rep (e.g. 'REP001').

    Returns:
        A narrative summary combining profile, performance, and pipeline data.
    """
    rep = REPS_DB.get(rep_id.upper())
    if not rep:
        return f"Rep ID '{rep_id}' not found."

    # Quota attainment calculation (inline — same logic as calculate_quota_attainment)
    quota = rep["quota_usd"]
    ytd = rep["ytd_sales_usd"]
    attainment_pct = (ytd / quota) * 100
    remaining = quota - ytd

    # Deals for this rep
    rep_deals = [d for d in DEALS_DB.values() if d["rep_id"].upper() == rep_id.upper()]
    open_deals = [d for d in rep_deals if d["stage"] != "Closed Won"]
    won_deals = [d for d in rep_deals if d["stage"] == "Closed Won"]

    summary = f"""
=== REP CONTEXT SUMMARY: {rep['name']} ({rep_id.upper()}) ===

PROFILE:
  • Territory: {rep['territory']}
  • Product Line: {rep['product_line']}
  • Manager: {rep['manager']}
  • Tenure: {rep['tenure_years']} years
  • Specializations: {', '.join(rep['specializations'])}
  • Top Accounts: {', '.join(rep['top_accounts'])}

PERFORMANCE:
  • Annual Quota: ${quota:,}
  • YTD Sales: ${ytd:,}
  • Attainment: {attainment_pct:.1f}%
  • Remaining to Quota: ${remaining:,}

PIPELINE:
  • Open Deals: {len(open_deals)}
  • Closed Won: {len(won_deals)}
  • Open Deal Stages: {', '.join(d['stage'] for d in open_deals) or 'None'}
""".strip()

    return summary
