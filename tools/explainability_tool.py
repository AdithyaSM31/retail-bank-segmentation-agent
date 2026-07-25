"""
Explainability Tool — Explains why customers belong to specific segments,
provides feature importance, and compares segments.
"""
import pandas as pd
import numpy as np
from langchain_core.tools import tool
from data_loader import get_customer_features
from tools.segmentation_tool import get_segment_results, _segment_method, _segment_rules


@tool
def explain_segment(segment_name: str) -> str:
    """
    Explain why customers were assigned to a particular segment.
    Shows the rules or distinguishing features that define this segment.
    
    Args:
        segment_name: Name of the segment to explain (e.g., 'Priority', 'Regular', 'Dormant',
                       or ML cluster names like 'High-Value Active (C0)')
    
    Returns: Detailed explanation of the segment's defining characteristics.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    # Try to find the segment (case-insensitive partial match)
    seg_col = "segment"
    all_segments = seg_data[seg_col].unique()
    matched = [s for s in all_segments if segment_name.lower() in s.lower()]

    if not matched:
        # Auto-recover if they are asking for a default dashboard KPI segment
        if segment_name.lower() in ["priority", "regular", "dormant"]:
            from tools.segmentation_tool import segment_customers_rule_based
            # Re-run default segmentation (without churn/risk keywords)
            segment_customers_rule_based.invoke("dashboard KPIs")
            seg_data = get_segment_results()
            all_segments = seg_data[seg_col].unique()
            matched = [s for s in all_segments if segment_name.lower() in s.lower()]
            
        if not matched:
            return f"Segment '{segment_name}' not found. Available segments: {list(all_segments)}"

    target_seg = matched[0]
    seg_subset = seg_data[seg_data[seg_col] == target_seg]
    other_data = seg_data[seg_data[seg_col] != target_seg]

    result = f"## Explanation: {target_seg} Segment\n\n"
    result += f"**Customers in segment:** {len(seg_subset):,} ({len(seg_subset)/len(seg_data)*100:.1f}%)\n\n"

    # If rule-based, show the rules
    from tools.segmentation_tool import _segment_rules as rules
    if rules and target_seg in rules:
        result += f"### Rules Used\n{rules[target_seg]}\n\n"

    # Show distinguishing features (compare segment vs rest)
    metrics = ["avg_balance", "total_transactions", "avg_amount", "total_amount",
               "recency_days", "txn_per_month", "max_balance", "std_amount", "age"]
    available = [m for m in metrics if m in seg_data.columns]

    result += "### Distinguishing Features (Segment vs. All Others)\n\n"
    result += "| Feature | Segment Avg | Others Avg | Difference | Direction |\n|---|---|---|---|---|\n"

    for m in available:
        seg_mean = seg_subset[m].mean()
        other_mean = other_data[m].mean()
        if other_mean != 0:
            diff_pct = ((seg_mean - other_mean) / abs(other_mean)) * 100
        else:
            diff_pct = 0
        direction = "↑ Higher" if diff_pct > 5 else ("↓ Lower" if diff_pct < -5 else "→ Similar")
        result += f"| {m} | {seg_mean:,.2f} | {other_mean:,.2f} | {diff_pct:+.1f}% | {direction} |\n"

    # Key insights
    result += "\n### Key Insights\n"
    for m in available:
        seg_mean = seg_subset[m].mean()
        other_mean = other_data[m].mean()
        if other_mean != 0:
            ratio = seg_mean / other_mean
            if ratio > 1.5:
                result += f"- **{target_seg}** customers have **{ratio:.1f}x higher** {m} than other segments\n"
            elif ratio < 0.67:
                result += f"- **{target_seg}** customers have **{1/ratio:.1f}x lower** {m} than other segments\n"

    return result


@tool
def explain_customer_segment(customer_id: str) -> str:
    """
    Explain why a specific customer was placed in their assigned segment.
    Shows the customer's feature values compared to segment averages and thresholds.
    
    Args:
        customer_id: The CustomerID to explain (e.g., 'C5841053')
    
    Returns: Customer-specific explanation with feature comparisons.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    cust_row = seg_data[seg_data["CustomerID"] == customer_id]
    if cust_row.empty:
        return f"Customer '{customer_id}' not found in the dataset."

    cust_row = cust_row.iloc[0]
    segment = cust_row["segment"]
    seg_subset = seg_data[seg_data["segment"] == segment]

    metrics = ["avg_balance", "total_transactions", "avg_amount", "recency_days",
               "txn_per_month", "max_balance", "std_amount"]
    available = [m for m in metrics if m in seg_data.columns]

    result = f"## Customer {customer_id} — Segment Explanation\n\n"
    result += f"**Assigned Segment:** {segment}\n\n"

    result += "### Feature Values vs. Segment Average\n\n"
    result += "| Feature | Customer Value | Segment Avg | Percentile in Segment |\n|---|---|---|---|\n"

    for m in available:
        cust_val = cust_row[m]
        seg_avg = seg_subset[m].mean()
        if pd.notna(cust_val):
            percentile = (seg_subset[m] <= cust_val).mean() * 100
            result += f"| {m} | {cust_val:,.2f} | {seg_avg:,.2f} | {percentile:.0f}th |\n"

    # Check rules
    from tools.segmentation_tool import _segment_rules as rules
    if rules and segment in rules:
        result += f"\n### Rule Applied\n{rules[segment]}\n"

    return result


@tool
def compare_segments(segment_a: str, segment_b: str) -> str:
    """
    Compare two customer segments side-by-side on all key metrics.
    Useful for understanding what differentiates one segment from another.
    
    Args:
        segment_a: Name of the first segment (e.g., 'Priority')
        segment_b: Name of the second segment (e.g., 'Regular')
    
    Returns: Side-by-side comparison table with all key metrics.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    all_segments = seg_data["segment"].unique()

    # Partial match
    match_a = [s for s in all_segments if segment_a.lower() in s.lower()]
    match_b = [s for s in all_segments if segment_b.lower() in s.lower()]

    if not match_a:
        return f"Segment '{segment_a}' not found. Available: {list(all_segments)}"
    if not match_b:
        return f"Segment '{segment_b}' not found. Available: {list(all_segments)}"

    seg_a_name = match_a[0]
    seg_b_name = match_b[0]

    data_a = seg_data[seg_data["segment"] == seg_a_name]
    data_b = seg_data[seg_data["segment"] == seg_b_name]

    metrics = ["avg_balance", "total_transactions", "avg_amount", "total_amount",
               "recency_days", "txn_per_month", "max_balance", "std_amount", "age"]
    available = [m for m in metrics if m in seg_data.columns]

    result = f"## Comparison: {seg_a_name} vs {seg_b_name}\n\n"
    result += f"| Metric | {seg_a_name} | {seg_b_name} | Difference |\n|---|---|---|---|\n"

    for m in available:
        mean_a = data_a[m].mean()
        mean_b = data_b[m].mean()
        diff = mean_a - mean_b
        result += f"| {m} | {mean_a:,.2f} | {mean_b:,.2f} | {diff:+,.2f} |\n"

    result += f"\n| **Count** | {len(data_a):,} | {len(data_b):,} | |\n"

    return result


@tool
def get_feature_importance_for_segments() -> str:
    """
    Calculate which features are most important in distinguishing between segments.
    Uses variance ratio (between-cluster variance / total variance) as a measure.
    Use this to understand what drives segmentation differences.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    metrics = ["avg_balance", "total_transactions", "avg_amount", "total_amount",
               "recency_days", "txn_per_month", "max_balance", "std_amount"]
    available = [m for m in metrics if m in seg_data.columns]

    importance = {}
    for m in available:
        overall_var = seg_data[m].var()
        if overall_var == 0:
            importance[m] = 0
            continue

        # Between-group variance
        group_means = seg_data.groupby("segment")[m].mean()
        overall_mean = seg_data[m].mean()
        group_sizes = seg_data.groupby("segment")[m].count()
        between_var = sum(group_sizes[g] * (group_means[g] - overall_mean) ** 2
                         for g in group_means.index) / len(seg_data)

        importance[m] = round(between_var / overall_var, 4)

    # Sort by importance
    sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)

    result = "## Feature Importance for Segmentation\n\n"
    result += "Higher scores indicate features that best distinguish between segments.\n\n"
    result += "| Rank | Feature | Importance Score | Interpretation |\n|---|---|---|---|\n"

    for rank, (feat, score) in enumerate(sorted_imp, 1):
        if score > 0.3:
            interp = "🔴 Critical differentiator"
        elif score > 0.1:
            interp = "🟡 Moderate differentiator"
        else:
            interp = "🟢 Weak differentiator"
        result += f"| {rank} | {feat} | {score} | {interp} |\n"

    return result
