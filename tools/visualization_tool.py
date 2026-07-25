"""
Visualization Tool — Generates interactive Plotly charts for customer segments,
distributions, comparisons, and correlations.
Returns Plotly figure JSON that Streamlit can render directly.
"""
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from langchain_core.tools import tool
from data_loader import get_customer_features, load_raw_data
from tools.segmentation_tool import get_segment_results
from config import CHARTS_DIR


def _save_and_return(fig, name: str) -> str:
    """Save chart as HTML and return the path."""
    path = CHARTS_DIR / f"{name}.html"
    fig.write_html(str(path), include_plotlyjs="cdn")
    # Also return JSON for Streamlit
    return json.dumps({
        "chart_type": name,
        "chart_path": str(path),
        "chart_json": fig.to_json(),
    })


@tool
def plot_segment_distribution() -> str:
    """
    Create a pie chart and bar chart showing the distribution of customers across segments.
    Use after segmentation to visualize segment sizes.
    Returns: Chart data as JSON (rendered automatically in the UI).
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first."

    seg_counts = seg_data["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]

    # Create subplots - stacked vertically
    fig = make_subplots(rows=2, cols=1,
                        specs=[[{"type": "domain"}], [{"type": "xy"}]],
                        subplot_titles=("Segment Distribution", "Customer Count by Segment"))

    # Pie chart
    fig.add_trace(go.Pie(labels=seg_counts['segment'], values=seg_counts['count'],
                         marker_colors=px.colors.qualitative.Set2,
                         textinfo="label+percent", hole=0.4), row=1, col=1)

    # Bar chart
    fig.add_trace(go.Bar(x=seg_counts['segment'], y=seg_counts['count'],
                         marker_color=px.colors.qualitative.Set2,
                         text=seg_counts['count'], textposition="auto"), row=2, col=1)

    fig.update_layout(
        title_text="Customer Segment Distribution",
        template="plotly_white",
        height=800,
        showlegend=False,
        font=dict(color="#1f2937"),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return _save_and_return(fig, "segment_distribution")


@tool
def plot_feature_comparison(feature_name: str) -> str:
    """
    Create box plots comparing a feature's distribution across all segments.
    Useful for understanding how a metric varies between segments.
    
    Args:
        feature_name: The feature to compare (e.g., 'avg_balance', 'total_transactions',
                       'avg_amount', 'recency_days', 'txn_per_month')
    
    Returns: Chart data as JSON.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet."

    if feature_name not in seg_data.columns:
        return f"Feature '{feature_name}' not found. Available: {list(seg_data.select_dtypes(include=[np.number]).columns)}"

    fig = px.box(seg_data, x="segment", y=feature_name, color="segment",
                 title=f"Distribution of {feature_name} by Segment",
                 template="plotly_white",
                 color_discrete_sequence=px.colors.qualitative.Set2)

    fig.update_layout(height=450, showlegend=False, font=dict(color="#1f2937"))

    return _save_and_return(fig, f"feature_comparison_{feature_name}")


@tool
def plot_cluster_scatter(x_feature: str, y_feature: str) -> str:
    """
    Create a 2D scatter plot showing customers colored by their segment.
    Great for visualizing how segments are distributed in feature space.
    
    Args:
        x_feature: Feature for x-axis (e.g., 'avg_balance')
        y_feature: Feature for y-axis (e.g., 'total_transactions')
    
    Returns: Chart data as JSON.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet."

    for f in [x_feature, y_feature]:
        if f not in seg_data.columns:
            return f"Feature '{f}' not found."

    # Sample for performance
    plot_data = seg_data.sample(n=min(5000, len(seg_data)), random_state=42)

    fig = px.scatter(plot_data, x=x_feature, y=y_feature, color="segment",
                     title=f"Customer Segments: {x_feature} vs {y_feature}",
                     template="plotly_white",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     opacity=0.6)

    fig.update_layout(height=500, font=dict(color="#1f2937"))

    return _save_and_return(fig, f"scatter_{x_feature}_vs_{y_feature}")


@tool
def plot_segment_radar() -> str:
    """
    Create a radar/spider chart showing the profile of each segment across key metrics.
    Each axis represents a normalized metric, showing relative strengths per segment.
    Use this for a holistic view of segment characteristics.
    Returns: Chart data as JSON.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet."

    metrics = ["avg_balance", "total_transactions", "avg_amount", "recency_days", "txn_per_month"]
    available = [m for m in metrics if m in seg_data.columns]

    # Normalize metrics to 0-1 for radar chart
    segments = seg_data["segment"].unique()
    fig = go.Figure()

    colors = px.colors.qualitative.Set2

    for i, seg in enumerate(segments):
        seg_subset = seg_data[seg_data["segment"] == seg]
        values = []
        for m in available:
            overall_max = seg_data[m].max()
            overall_min = seg_data[m].min()
            if overall_max != overall_min:
                normalized = (seg_subset[m].mean() - overall_min) / (overall_max - overall_min)
            else:
                normalized = 0.5
            values.append(round(normalized, 3))

        # Close the radar
        values.append(values[0])
        labels = available + [available[0]]

        fig.add_trace(go.Scatterpolar(
            r=values, theta=labels, fill="toself",
            name=seg, line_color=colors[i % len(colors)],
            opacity=0.7
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Segment Profiles (Radar Chart)",
        template="plotly_white",
        height=500,
        font=dict(color="#1f2937")
    )

    return _save_and_return(fig, "segment_radar")


@tool
def plot_correlation_heatmap() -> str:
    """
    Create a correlation heatmap of customer-level numerical features.
    Shows which features are positively or negatively correlated.
    Returns: Chart data as JSON.
    """
    cust = get_customer_features()
    num_cols = ["total_transactions", "total_amount", "avg_amount", "avg_balance",
                "max_balance", "recency_days", "std_amount", "txn_per_month", "age"]
    available = [c for c in num_cols if c in cust.columns]

    corr = cust[available].corr().round(3)

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=available,
        y=available,
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        text=corr.values.round(2),
        texttemplate="%{text}",
        textfont={"size": 10},
    ))

    fig.update_layout(
        title="Feature Correlation Heatmap",
        template="plotly_white",
        height=500,
        width=600,
        font=dict(color="#1f2937")
    )

    return _save_and_return(fig, "correlation_heatmap")


@tool
def plot_monthly_trends() -> str:
    """
    Create a dual-axis chart showing the monthly transaction trends (volume and total amount).
    Use this specifically when the user asks for Monthly Trends Analysis.
    Returns: Chart data as JSON.
    """
    raw_df = load_raw_data()
    if raw_df is None or raw_df.empty:
        return "No transaction data available."

    # Group by month
    raw_df['YearMonth_sort'] = raw_df['TransactionDate'].dt.to_period('M')
    monthly_stats = raw_df.groupby('YearMonth_sort').agg(
        TotalTransactions=('TransactionID', 'count'),
        TotalVolume=('TransactionAmount', 'sum')
    ).reset_index().sort_values('YearMonth_sort')
    
    # Format beautifully for display (e.g. "Aug 2016")
    monthly_stats['MonthLabel'] = monthly_stats['YearMonth_sort'].dt.strftime('%b %Y')

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(x=monthly_stats['MonthLabel'], y=monthly_stats['TotalTransactions'],
                         name="Total Transactions", marker_color="#3b82f6"),
                  secondary_y=False)

    fig.add_trace(go.Scatter(x=monthly_stats['MonthLabel'], y=monthly_stats['TotalVolume'],
                             name="Total Volume (INR)", marker_color="#10b981", mode="lines+markers"),
                  secondary_y=True)

    fig.update_layout(
        title_text="Monthly Transaction Trends",
        template="plotly_white",
        height=500,
        font=dict(color="#1f2937"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(type='category', title_text="Month")
    fig.update_yaxes(title_text="Total Transactions", secondary_y=False)
    fig.update_yaxes(title_text="Total Volume (INR)", secondary_y=True)

    return _save_and_return(fig, "monthly_trends")
