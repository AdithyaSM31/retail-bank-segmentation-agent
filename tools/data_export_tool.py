"""
Data Export Tool — Exports segmentation results, reports, and analysis data to CSV/text files.
"""
import pandas as pd
from langchain_core.tools import tool
from tools.segmentation_tool import get_segment_results
from data_loader import get_customer_features
from config import OUTPUT_DIR


@tool
def export_segments_to_csv() -> str:
    """
    Export the current customer segmentation results to a CSV file.
    The CSV includes CustomerID, segment label, and key features.
    Use after segmentation to provide downloadable results to the user.
    Returns: Path to the exported CSV file.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    export_cols = ["CustomerID", "segment", "avg_balance", "total_transactions",
                   "avg_amount", "total_amount", "recency_days", "txn_per_month",
                   "max_balance", "gender", "location", "age"]
    available = [c for c in export_cols if c in seg_data.columns]

    path = OUTPUT_DIR / "customer_segments.csv"
    seg_data[available].to_csv(path, index=False)

    counts = seg_data["segment"].value_counts()
    result = f"## Segments Exported\n\n"
    result += f"**File:** customer_segments.csv\n"
    result += f"**Total Customers:** {len(seg_data):,}\n"
    result += f"**Columns:** {available}\n\n"
    result += "### Segment Counts\n"
    for seg, count in counts.items():
        result += f"- {seg}: {count:,}\n"

    return result


@tool
def export_segment_report() -> str:
    """
    Generate and export a comprehensive text report of the segmentation analysis.
    Includes segment descriptions, key metrics, and recommendations.
    Returns: The full report as text + path to the saved file.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    segments = seg_data["segment"].unique()

    report = "# Customer Segmentation Report\n\n"
    report += f"**Total Customers Analyzed:** {len(seg_data):,}\n"
    report += f"**Number of Segments:** {len(segments)}\n\n"

    for seg in sorted(segments):
        subset = seg_data[seg_data["segment"] == seg]
        report += f"## Segment: {seg}\n\n"
        report += f"- **Size:** {len(subset):,} customers ({len(subset)/len(seg_data)*100:.1f}%)\n"

        metrics = ["avg_balance", "total_transactions", "avg_amount", "recency_days", "txn_per_month"]
        for m in metrics:
            if m in subset.columns:
                report += f"- **Avg {m}:** {subset[m].mean():,.2f}\n"

        # Gender distribution
        if "gender" in subset.columns:
            gender_dist = subset["gender"].value_counts().to_dict()
            report += f"- **Gender:** {gender_dist}\n"

        report += "\n"

    # Save report
    path = OUTPUT_DIR / "segmentation_report.md"
    with open(path, "w") as f:
        f.write(report)

    return report + f"\n**Report saved to:** segmentation_report.md"


@tool
def query_segment_data(segment_name: str, query_description: str) -> str:
    """
    Query and filter data for a specific segment. Performs aggregation or filtering
    based on the query description.
    
    Args:
        segment_name: Name of the segment to query (e.g., 'Priority', 'Regular')
        query_description: What to compute — one of: 'average_transactions', 'top_customers', 
                          'demographics', 'transaction_summary', 'balance_distribution'
    
    Returns: Formatted query results.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet."

    all_segments = seg_data["segment"].unique()
    matched = [s for s in all_segments if segment_name.lower() in s.lower()]
    if not matched:
        return f"Segment '{segment_name}' not found. Available: {list(all_segments)}"

    seg_label = matched[0]
    subset = seg_data[seg_data["segment"] == seg_label]

    query_lower = query_description.lower()

    if "average" in query_lower or "mean" in query_lower or "transaction" in query_lower:
        result = f"## Transaction Statistics: {seg_label}\n\n"
        result += f"- **Avg Transaction Amount:** ₹{subset['avg_amount'].mean():,.2f}\n"
        result += f"- **Total Transactions (avg):** {subset['total_transactions'].mean():,.1f}\n"
        result += f"- **Total Amount (avg):** ₹{subset['total_amount'].mean():,.2f}\n"
        result += f"- **Transactions/Month (avg):** {subset['txn_per_month'].mean():,.2f}\n"
        if "max_amount" in subset.columns:
            result += f"- **Max Single Transaction (avg):** ₹{subset['max_amount'].mean():,.2f}\n"
        return result

    elif "top" in query_lower or "best" in query_lower:
        top = subset.nlargest(10, "total_amount")
        result = f"## Top 10 Customers in {seg_label}\n\n"
        result += "| CustomerID | Total Amount | Avg Balance | Transactions |\n|---|---|---|---|\n"
        for _, row in top.iterrows():
            result += f"| {row['CustomerID']} | ₹{row['total_amount']:,.2f} | ₹{row['avg_balance']:,.2f} | {row['total_transactions']:,} |\n"
        return result

    elif "demograph" in query_lower:
        result = f"## Demographics: {seg_label}\n\n"
        if "gender" in subset.columns:
            result += f"### Gender Distribution\n{subset['gender'].value_counts().to_string()}\n\n"
        if "age" in subset.columns:
            result += f"### Age Statistics\n{subset['age'].describe().round(1).to_string()}\n\n"
        if "location" in subset.columns:
            result += f"### Top Locations\n{subset['location'].value_counts().head(10).to_string()}\n"
        return result

    elif "balance" in query_lower:
        result = f"## Balance Distribution: {seg_label}\n\n"
        result += f"- **Mean:** ₹{subset['avg_balance'].mean():,.2f}\n"
        result += f"- **Median:** ₹{subset['avg_balance'].median():,.2f}\n"
        result += f"- **Std Dev:** ₹{subset['avg_balance'].std():,.2f}\n"
        result += f"- **Min:** ₹{subset['avg_balance'].min():,.2f}\n"
        result += f"- **Max:** ₹{subset['avg_balance'].max():,.2f}\n"
        return result

    else:
        # General summary
        result = f"## Summary: {seg_label}\n\n"
        result += subset.describe().round(2).to_string()
        return result
