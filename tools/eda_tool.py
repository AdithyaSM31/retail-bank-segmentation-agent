"""
EDA Tool — Performs automated exploratory data analysis on the bank customer dataset.
Returns structured text summaries that the LLM can interpret and relay to the user.
"""
import pandas as pd
import numpy as np
from langchain_core.tools import tool
from data_loader import load_raw_data, get_customer_features, get_data_summary


@tool
def run_full_eda() -> str:
    """
    Run a comprehensive exploratory data analysis on the bank transactions dataset.
    Returns a summary of the dataset including shape, column types, missing values,
    summary statistics for numerical columns, and value counts for categorical columns.
    Use this when the user asks for a general overview or EDA of the data.
    """
    df = load_raw_data()
    summary = get_data_summary()

    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_report = missing[missing > 0]

    # Numerical stats
    num_stats = df.describe().round(2).to_string()

    # Categorical stats
    gender_dist = df["CustGender"].value_counts().to_dict()
    top_locations = df["CustLocation"].value_counts().head(10).to_dict()

    # Transaction amount stats
    txn_stats = {
        "mean": round(df["TransactionAmount"].mean(), 2),
        "median": round(df["TransactionAmount"].median(), 2),
        "std": round(df["TransactionAmount"].std(), 2),
        "min": round(df["TransactionAmount"].min(), 2),
        "max": round(df["TransactionAmount"].max(), 2),
    }

    # Balance stats
    bal_stats = {
        "mean": round(df["CustAccountBalance"].mean(), 2),
        "median": round(df["CustAccountBalance"].median(), 2),
        "std": round(df["CustAccountBalance"].std(), 2),
        "min": round(df["CustAccountBalance"].min(), 2),
        "max": round(df["CustAccountBalance"].max(), 2),
    }

    result = f"""## EDA Summary

**Dataset Shape:** {summary['shape'][0]:,} rows × {summary['shape'][1]} columns
**Unique Customers:** {summary['unique_customers']:,}
**Date Range:** {summary['date_range']}

### Columns & Types
{chr(10).join(f"- **{col}**: {dtype}" for col, dtype in summary['dtypes'].items())}

### Missing Values
{chr(10).join(f"- **{col}**: {count:,} ({missing_pct[col]}%)" for col, count in missing_report.items()) if len(missing_report) > 0 else "No missing values in critical columns."}

### Transaction Amount Statistics
- Mean: ₹{txn_stats['mean']:,.2f}
- Median: ₹{txn_stats['median']:,.2f}
- Std Dev: ₹{txn_stats['std']:,.2f}
- Min: ₹{txn_stats['min']:,.2f} | Max: ₹{txn_stats['max']:,.2f}

### Account Balance Statistics
- Mean: ₹{bal_stats['mean']:,.2f}
- Median: ₹{bal_stats['median']:,.2f}
- Std Dev: ₹{bal_stats['std']:,.2f}
- Min: ₹{bal_stats['min']:,.2f} | Max: ₹{bal_stats['max']:,.2f}

### Gender Distribution
{chr(10).join(f"- {g}: {c:,}" for g, c in gender_dist.items())}

### Top 10 Customer Locations
{chr(10).join(f"- {loc}: {c:,}" for loc, c in top_locations.items())}
"""
    return result


@tool
def get_column_distribution(column_name: str) -> str:
    """
    Get the distribution statistics for a specific column in the dataset.
    Returns percentiles, mean, median, mode, and value counts for categorical columns.
    Use when the user asks about the distribution of a specific variable.
    Args:
        column_name: The exact column name to analyze (e.g., 'TransactionAmount', 'CustAccountBalance', 'CustGender')
    """
    df = load_raw_data()
    if column_name not in df.columns:
        # Try matching customer features
        cust = get_customer_features()
        if column_name in cust.columns:
            df = cust
        else:
            return f"Column '{column_name}' not found. Available columns: {list(df.columns)}"

    col = df[column_name]
    if pd.api.types.is_numeric_dtype(col):
        stats = col.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.99]).round(2)
        result = f"## Distribution of {column_name}\n\n"
        result += f"- **Count:** {stats['count']:,.0f}\n"
        result += f"- **Mean:** {stats['mean']:,.2f}\n"
        result += f"- **Std:** {stats['std']:,.2f}\n"
        result += f"- **Min:** {stats['min']:,.2f}\n"
        result += f"- **10th percentile:** {stats['10%']:,.2f}\n"
        result += f"- **25th percentile:** {stats['25%']:,.2f}\n"
        result += f"- **Median (50th):** {stats['50%']:,.2f}\n"
        result += f"- **75th percentile:** {stats['75%']:,.2f}\n"
        result += f"- **90th percentile:** {stats['90%']:,.2f}\n"
        result += f"- **99th percentile:** {stats['99%']:,.2f}\n"
        result += f"- **Max:** {stats['max']:,.2f}\n"
        result += f"- **Skewness:** {col.skew():.4f}\n"
        result += f"- **Kurtosis:** {col.kurtosis():.4f}\n"
        return result
    else:
        vc = col.value_counts().head(20)
        result = f"## Distribution of {column_name} (Top 20)\n\n"
        for val, count in vc.items():
            result += f"- **{val}**: {count:,} ({count/len(col)*100:.1f}%)\n"
        return result


@tool
def get_correlation_analysis() -> str:
    """
    Compute the correlation matrix between key numerical features of customers.
    Returns a formatted correlation matrix showing relationships between balance,
    transaction amount, frequency, recency, and other features.
    Use when the user asks about correlations or relationships between variables.
    """
    cust = get_customer_features()
    num_cols = ["total_transactions", "total_amount", "avg_amount", "avg_balance",
                "max_balance", "recency_days", "std_amount", "txn_per_month", "age"]
    available = [c for c in num_cols if c in cust.columns]
    corr = cust[available].corr().round(3)

    result = "## Correlation Matrix (Customer-Level Features)\n\n"
    result += "| Feature | " + " | ".join(available) + " |\n"
    result += "|" + "---|" * (len(available) + 1) + "\n"
    for idx in available:
        row = f"| **{idx}** | "
        row += " | ".join(str(corr.loc[idx, c]) for c in available)
        row += " |"
        result += row + "\n"

    # Highlight strong correlations
    result += "\n### Notable Correlations\n"
    seen = set()
    for i, c1 in enumerate(available):
        for c2 in available[i+1:]:
            val = corr.loc[c1, c2]
            key = tuple(sorted([c1, c2]))
            if abs(val) > 0.5 and key not in seen:
                direction = "positive" if val > 0 else "negative"
                result += f"- **{c1}** ↔ **{c2}**: {val} (strong {direction})\n"
                seen.add(key)

    return result


@tool
def filter_and_aggregate(group_by: str, agg_column: str, agg_function: str) -> str:
    """
    Perform a group-by aggregation on the customer features dataset.
    Use this to answer questions like 'What is the average balance per gender?' or
    'What is the total transaction amount by location?'.
    Args:
        group_by: Column to group by (e.g., 'gender', 'location', 'segment')
        agg_column: Column to aggregate (e.g., 'avg_balance', 'total_amount', 'total_transactions')
        agg_function: Aggregation function — one of 'mean', 'sum', 'count', 'median', 'min', 'max'
    """
    cust = get_customer_features()
    if group_by not in cust.columns:
        return f"Column '{group_by}' not found. Available: {list(cust.columns)}"
    if agg_column not in cust.columns:
        return f"Column '{agg_column}' not found. Available: {list(cust.columns)}"
    if agg_function not in ["mean", "sum", "count", "median", "min", "max"]:
        return "Invalid agg_function. Use one of: mean, sum, count, median, min, max"

    result_df = cust.groupby(group_by)[agg_column].agg(agg_function).round(2)
    result_df = result_df.sort_values(ascending=False)

    result = f"## {agg_function.title()} of {agg_column} by {group_by}\n\n"
    result += f"| {group_by} | {agg_function}({agg_column}) |\n|---|---|\n"
    for idx, val in result_df.head(30).items():
        result += f"| {idx} | {val:,.2f} |\n"

    if len(result_df) > 30:
        result += f"\n*Showing top 30 of {len(result_df)} groups.*\n"

    return result


@tool
def get_missing_value_report() -> str:
    """
    Generate a detailed missing value analysis for the raw dataset.
    Shows counts and percentages of missing values per column.
    Use when the user asks about data quality or missing data.
    """
    df = load_raw_data()
    total = len(df)
    missing = df.isnull().sum().sort_values(ascending=False)

    result = "## Missing Value Report\n\n"
    result += f"**Total Records:** {total:,}\n\n"
    result += "| Column | Missing Count | Missing % | Status |\n|---|---|---|---|\n"
    for col, count in missing.items():
        pct = count / total * 100
        status = "✅ OK" if pct == 0 else ("⚠️ Low" if pct < 5 else "🔴 High")
        result += f"| {col} | {count:,} | {pct:.2f}% | {status} |\n"

    return result
