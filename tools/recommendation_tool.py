"""
Recommendation Tool — Generates personalized banking product recommendations,
identifies upgrade candidates, and provides retention strategies.
"""
import pandas as pd
import numpy as np
from langchain_core.tools import tool
from data_loader import get_customer_features, load_synthetic_products
from tools.segmentation_tool import get_segment_results


# Product recommendation rules mapped to segment profiles
PRODUCT_RECOMMENDATIONS = {
    "Priority": {
        "products": [
            "Premium Credit Card (Platinum/Black) with high credit limit and travel rewards",
            "Wealth Management & Portfolio Advisory Services",
            "Premium Savings Account with higher interest rates",
            "Personal Relationship Manager",
            "Priority Banking Lounge access",
            "Investment products: Mutual Funds, Fixed Deposits, SIPs",
        ],
        "strategies": [
            "Offer exclusive invitations to financial planning workshops",
            "Provide dedicated relationship manager for personalized service",
            "Cross-sell investment and insurance products",
            "Offer premium debit/credit cards with lifestyle benefits",
        ],
    },
    "Regular": {
        "products": [
            "Standard Credit Card with cashback rewards",
            "Personal Loan at competitive interest rates",
            "Recurring Deposit (RD) for savings habit building",
            "Systematic Investment Plan (SIP) for wealth building",
            "Mobile Banking premium features",
        ],
        "strategies": [
            "Encourage higher balance maintenance through incentive programs",
            "Promote SIP and RD products for long-term wealth building",
            "Offer credit cards with spend-based reward programs",
            "Send personalized financial tips and product awareness campaigns",
        ],
    },
    "Dormant": {
        "products": [
            "Zero-balance Savings Account to reduce friction",
            "Basic Credit Card with low annual fee",
            "Fixed Deposit for parking idle funds",
            "Digital-only banking with minimal charges",
        ],
        "strategies": [
            "Re-engagement campaigns with personalized offers",
            "Waive dormant account charges for reactivation",
            "Offer cashback on first 5 transactions post-reactivation",
            "Send SMS/email alerts about new features and benefits",
            "Simplify onboarding for digital banking services",
        ],
    },
}

# Fallback for ML-based segments
ML_SEGMENT_MAPPING = {
    "high-value": "Priority",
    "active": "Priority",
    "regular": "Regular",
    "low-balance": "Regular",
    "dormant": "Dormant",
    "inactive": "Dormant",
}


def _map_segment_to_category(segment_name: str) -> str:
    """Map any segment name to a standard category for recommendations."""
    lower = segment_name.lower()
    for keyword, category in ML_SEGMENT_MAPPING.items():
        if keyword in lower:
            return category
    return "Regular"  # Default


@tool
def recommend_products_for_segment(segment_name: str) -> str:
    """
    Get personalized banking product recommendations for a specific customer segment.
    Provides product suggestions and strategies tailored to the segment's profile.
    
    Args:
        segment_name: Name of the segment (e.g., 'Priority', 'Regular', 'Dormant',
                       or ML cluster names — they will be mapped automatically)
    
    Returns: Product recommendations and strategies for the segment.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    # Map to standard category
    category = _map_segment_to_category(segment_name)
    recs = PRODUCT_RECOMMENDATIONS.get(category, PRODUCT_RECOMMENDATIONS["Regular"])

    # Get segment stats
    all_segments = seg_data["segment"].unique()
    matched = [s for s in all_segments if segment_name.lower() in s.lower()]
    seg_label = matched[0] if matched else segment_name

    seg_subset = seg_data[seg_data["segment"] == seg_label] if matched else pd.DataFrame()

    result = f"## Product Recommendations: {seg_label}\n\n"

    if not seg_subset.empty:
        result += f"**Segment Size:** {len(seg_subset):,} customers\n"
        result += f"**Avg Balance:** ₹{seg_subset['avg_balance'].mean():,.2f}\n"
        result += f"**Avg Transactions:** {seg_subset['total_transactions'].mean():,.1f}\n\n"

    result += "### Recommended Products\n"
    for i, product in enumerate(recs["products"], 1):
        result += f"{i}. {product}\n"

    result += "\n### Engagement Strategies\n"
    for i, strategy in enumerate(recs["strategies"], 1):
        result += f"{i}. {strategy}\n"

    return result


@tool
def identify_upgrade_candidates(from_segment: str, to_segment: str) -> str:
    """
    Identify customers in one segment who have potential to move to a higher segment.
    Finds customers whose metrics are close to the target segment's thresholds.
    
    Args:
        from_segment: Source segment (e.g., 'Regular')
        to_segment: Target segment (e.g., 'Priority')
    
    Returns: List of upgrade candidate customers with recommendations for conversion.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    all_segments = seg_data["segment"].unique()
    match_from = [s for s in all_segments if from_segment.lower() in s.lower()]
    match_to = [s for s in all_segments if to_segment.lower() in s.lower()]

    if not match_from:
        return f"Segment '{from_segment}' not found. Available: {list(all_segments)}"
    if not match_to:
        return f"Segment '{to_segment}' not found. Available: {list(all_segments)}"

    from_name = match_from[0]
    to_name = match_to[0]

    from_data = seg_data[seg_data["segment"] == from_name].copy()
    to_data = seg_data[seg_data["segment"] == to_name]

    if from_data.empty or to_data.empty:
        return "One or both segments are empty."

    # Key metrics to compare
    key_metrics = ["avg_balance", "total_transactions", "txn_per_month", "avg_amount"]
    available = [m for m in key_metrics if m in seg_data.columns]

    # Calculate thresholds: use the 25th percentile of the target segment
    thresholds = {}
    for m in available:
        thresholds[m] = to_data[m].quantile(0.25)

    # Score each customer in from_segment by proximity to target thresholds
    from_data["upgrade_score"] = 0
    for m in available:
        threshold = thresholds[m]
        if m == "recency_days":
            # Lower recency is better
            from_data["upgrade_score"] += (from_data[m] <= threshold).astype(int)
        else:
            from_data["upgrade_score"] += (from_data[m] >= threshold * 0.7).astype(int)

    # Top candidates: meet at least half the criteria
    min_score = max(1, len(available) // 2)
    candidates = from_data[from_data["upgrade_score"] >= min_score].sort_values(
        "upgrade_score", ascending=False
    )

    result = f"## Upgrade Candidates: {from_name} → {to_name}\n\n"
    result += f"**Total in {from_name}:** {len(from_data):,}\n"
    result += f"**Potential Candidates:** {len(candidates):,} ({len(candidates)/len(from_data)*100:.1f}%)\n\n"

    result += "### Target Thresholds (25th percentile of target segment)\n"
    for m, t in thresholds.items():
        result += f"- {m}: {t:,.2f}\n"

    result += f"\n### Top 20 Candidates\n"
    result += "| CustomerID | Score |"
    for m in available:
        result += f" {m} |"
    result += "\n|" + "---|" * (2 + len(available)) + "\n"

    for _, row in candidates.head(20).iterrows():
        result += f"| {row['CustomerID']} | {row['upgrade_score']}/{len(available)} |"
        for m in available:
            result += f" {row[m]:,.2f} |"
        result += "\n"

    # Recommendations for conversion
    result += f"\n### Recommendations to Convert {from_name} → {to_name}\n"
    category_from = _map_segment_to_category(from_name)
    category_to = _map_segment_to_category(to_name)

    if category_to == "Priority":
        result += """
1. **Increase balance incentives**: Offer higher interest rates for maintaining balance above threshold
2. **Transaction rewards**: Provide cashback/rewards for increasing transaction frequency
3. **Exclusive previews**: Give early access to priority banking features as motivation
4. **Personalized outreach**: Assign relationship managers to high-potential candidates
5. **Milestone rewards**: Create a tiered reward system for progressive balance/activity growth
6. **SIP/RD products**: Recommend systematic investment plans to build balance gradually
"""
    else:
        result += """
1. **Re-engagement campaigns**: Send personalized offers to increase activity
2. **Reduced fees**: Waive transaction charges temporarily to encourage usage
3. **Product bundling**: Offer product bundles at discounted rates
4. **Financial literacy**: Share financial tips and planning resources
"""

    return result


@tool
def get_retention_strategies(segment_name: str) -> str:
    """
    Get customer retention strategies for a specific segment.
    Provides tailored strategies to prevent customer churn based on segment characteristics.
    
    Args:
        segment_name: Name of the segment (e.g., 'Dormant', 'Regular', 'Priority')
    
    Returns: Retention strategies tailored to the segment's risk profile.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    all_segments = seg_data["segment"].unique()
    matched = [s for s in all_segments if segment_name.lower() in s.lower()]
    seg_label = matched[0] if matched else segment_name
    category = _map_segment_to_category(seg_label)

    seg_subset = seg_data[seg_data["segment"] == seg_label] if matched else pd.DataFrame()

    result = f"## Retention Strategies: {seg_label}\n\n"

    if not seg_subset.empty:
        avg_recency = seg_subset["recency_days"].mean() if "recency_days" in seg_subset.columns else 0
        result += f"**Customers:** {len(seg_subset):,}\n"
        result += f"**Avg Recency:** {avg_recency:.0f} days\n"
        result += f"**Churn Risk:** {'🔴 High' if avg_recency > 90 else ('🟡 Medium' if avg_recency > 30 else '🟢 Low')}\n\n"

    strategies = {
        "Priority": [
            "**Proactive service**: Regular check-ins from dedicated relationship manager",
            "**Exclusive benefits**: VIP events, airport lounge access, lifestyle rewards",
            "**Portfolio reviews**: Quarterly investment review sessions",
            "**Rate matching**: Competitive rates on loans and deposits to prevent attrition",
            "**Family banking**: Extend benefits to family members",
            "**Complaint resolution**: Priority handling of all service requests within 24 hours",
        ],
        "Regular": [
            "**Upgrade path**: Show clear benefits of moving to Priority tier",
            "**Reward loyalty**: Points-based system for long tenure customers",
            "**Digital engagement**: Push notifications for relevant offers and services",
            "**Financial planning**: Free basic financial health checks annually",
            "**Feedback loops**: Regular satisfaction surveys with action follow-ups",
        ],
        "Dormant": [
            "**Win-back campaigns**: Personalized emails with compelling reactivation offers",
            "**Fee waivers**: Waive dormancy charges for 6 months on reactivation",
            "**Simplified access**: Promote easy-to-use mobile banking features",
            "**Incentive deposits**: Offer bonus interest on first deposit post-reactivation",
            "**Root cause analysis**: Survey to understand reasons for inactivity",
            "**Progressive activation**: Small rewards for incremental engagement milestones",
        ],
    }

    result += "### Recommended Retention Strategies\n\n"
    for i, strategy in enumerate(strategies.get(category, strategies["Regular"]), 1):
        result += f"{i}. {strategy}\n"

    return result
