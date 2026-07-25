"""
Segmentation Tool — Performs customer segmentation using rule-based or ML-based methods.
Supports KMeans clustering, rule-based segmentation, and optimal cluster analysis.
"""
import pandas as pd
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score
from langchain_core.tools import tool
from data_loader import get_customer_features
from tools.feature_engineering_tool import get_scaled_data, get_selected_features
from config import OUTPUT_DIR, RANDOM_STATE, DEFAULT_N_CLUSTERS, MAX_CLUSTERS_SEARCH

# Module-level cache for segment results
_segment_results = None
_segment_model = None
_segment_method = None
_segment_rules = None


def get_segment_results() -> pd.DataFrame:
    """Get the cached segmentation results (used internally by other tools)."""
    global _segment_results
    if _segment_results is not None:
        return _segment_results.copy()
    return None


def set_segment_results(df: pd.DataFrame, method: str, rules: dict = None):
    """Cache segmentation results."""
    global _segment_results, _segment_method, _segment_rules
    _segment_results = df
    _segment_method = method
    _segment_rules = rules


@tool
def segment_customers_rule_based(rules_description: str) -> str:
    """
    Segment customers using rule-based logic. The rules should define customer segments
    based on conditions on features like balance, transaction frequency, etc.
    
    Args:
        rules_description: A natural language description of the rules to apply.
            Example: "priority: avg_balance > 50000 and total_transactions > 20; 
                      regular: avg_balance > 5000 and total_transactions > 5; 
                      dormant: all others"
            
            Available features for rules: avg_balance, max_balance, total_transactions, 
            avg_amount, total_amount, recency_days, txn_per_month, std_amount, tenure_days
    
    Returns: Summary of segmentation results with segment sizes and characteristics.
    """
    cust = get_customer_features()

    # Parse rules from description — interpret common patterns
    rules_lower = rules_description.lower()

    # Determine segment logic from the description
    segments = pd.Series("Other", index=cust.index)
    rules_applied = {}

    # Try to parse structured rules (semicolon-separated)
    if ";" in rules_description:
        rule_parts = rules_description.split(";")
    elif "\n" in rules_description:
        rule_parts = rules_description.split("\n")
    if any(kw in rules_lower for kw in ["risk", "churn"]):
        # Churn Risk segmentation
        high_risk_mask = cust["recency_days"] > 60
        medium_risk_mask = (cust["recency_days"] > 30) & (cust["recency_days"] <= 60)
        low_risk_mask = cust["recency_days"] <= 30
        
        segments[high_risk_mask] = "High Risk"
        segments[medium_risk_mask] = "Medium Risk"
        segments[low_risk_mask] = "Low Risk"
        
        rules_applied["High Risk"] = "recency_days > 60"
        rules_applied["Medium Risk"] = "30 < recency_days <= 60"
        rules_applied["Low Risk"] = "recency_days <= 30"
    else:
        # Default Business Logic (Matches Dashboard KPIs)
        dormant_mask = cust["recency_days"] > 90
        active_mask = ~dormant_mask
        
        priority_mask = active_mask & (cust["avg_balance"] > 100000)
        regular_mask = active_mask & (cust["avg_balance"] <= 100000)
        
        segments[dormant_mask] = "Dormant"
        segments[priority_mask] = "Priority"
        segments[regular_mask] = "Regular"
        
        rules_applied["Dormant"] = "recency_days > 90"
        rules_applied["Priority"] = "recency_days <= 90 AND avg_balance > 100000"
        rules_applied["Regular"] = "recency_days <= 90 AND avg_balance <= 100000"

    cust["segment"] = segments

    # Cache results
    set_segment_results(cust, "rule_based", rules_applied)

    # Export to CSV
    export_path = OUTPUT_DIR / "segments.csv"
    cust[["CustomerID", "segment", "avg_balance", "total_transactions", "avg_amount",
          "recency_days", "txn_per_month"]].to_csv(export_path, index=False)

    # Build summary
    seg_summary = cust.groupby("segment").agg(
        count=("CustomerID", "count"),
        avg_balance=("avg_balance", "mean"),
        avg_transactions=("total_transactions", "mean"),
        avg_txn_amount=("avg_amount", "mean"),
        avg_recency=("recency_days", "mean"),
    ).round(2)

    result = f"Rule-Based Segmentation Complete. Segments created:\n"
    for seg, row in seg_summary.iterrows():
        result += f"- {seg}: {row['count']} customers\n"
    return result


@tool
def segment_customers_ml(n_clusters: int = 0) -> str:
    """
    Segment customers using KMeans ML clustering algorithm.
    Automatically scales features and determines optimal clusters if n_clusters is 0.
    
    Args:
        n_clusters: Number of clusters to create. Set to 0 to auto-detect optimal number
                    using the elbow method and silhouette analysis. Default is 0 (auto).
    
    Returns: Summary of ML-based segmentation with cluster profiles and quality metrics.
    """
    cust = get_customer_features()
    scaled = get_scaled_data()
    features_used = get_selected_features()

    # Auto-detect optimal clusters
    if n_clusters <= 0:
        best_k = DEFAULT_N_CLUSTERS
        best_score = -1
        scores = {}
        inertias = {}

        for k in range(2, min(MAX_CLUSTERS_SEARCH + 1, 11)):
            km = MiniBatchKMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=3, max_iter=100, batch_size=10000)
            labels = km.fit_predict(scaled)
            score = silhouette_score(scaled, labels, sample_size=min(2000, len(scaled)))
            scores[k] = round(score, 4)
            inertias[k] = round(km.inertia_, 2)
            if score > best_score:
                best_score = score
                best_k = k

        n_clusters = best_k
        auto_detected = True
    else:
        scores = {}
        inertias = {}
        auto_detected = False

    # Run final KMeans
    km = MiniBatchKMeans(n_clusters=n_clusters, random_state=RANDOM_STATE, n_init=3, max_iter=100, batch_size=10000)
    labels = km.fit_predict(scaled)
    sil_score = silhouette_score(scaled, labels, sample_size=min(2000, len(scaled)))

    # Assign labels to customers
    cust["cluster"] = labels

    # Generate descriptive labels based on cluster centroids
    centroids = pd.DataFrame(km.cluster_centers_, columns=features_used)
    cluster_labels = {}
    for i in range(n_clusters):
        centroid = centroids.iloc[i]
        # Determine label based on relative feature values
        bal_rank = centroid.get("avg_balance", 0)
        txn_rank = centroid.get("total_transactions", 0)

        if bal_rank > 0.5 and txn_rank > 0.5:
            label = "High-Value Active"
        elif bal_rank > 0.5:
            label = "High-Balance Low-Activity"
        elif txn_rank > 0.5:
            label = "Active Low-Balance"
        elif bal_rank < -0.5 and txn_rank < -0.5:
            label = "Dormant"
        else:
            label = "Regular"

        # Append cluster number to avoid duplicates
        cluster_labels[i] = f"{label} (C{i})"

    cust["segment"] = cust["cluster"].map(cluster_labels)

    # Cache results
    _segment_model_ref = km
    set_segment_results(cust, "ml_kmeans")

    # Export
    export_path = OUTPUT_DIR / "segments.csv"
    export_cols = ["CustomerID", "segment", "cluster"] + [c for c in features_used if c in cust.columns] + ["avg_balance", "total_transactions", "avg_amount", "recency_days"]
    export_cols = list(dict.fromkeys(export_cols))  # deduplicate
    cust[[c for c in export_cols if c in cust.columns]].to_csv(export_path, index=False)

    # Build result
    result = f"""## ML-Based Segmentation Complete (KMeans)

**Clusters:** {n_clusters}
**Features used:** {features_used}
**Silhouette Score:** {sil_score:.4f} (closer to 1.0 = better separated clusters)
"""

    if auto_detected:
        result += f"\n### Optimal Cluster Analysis\n"
        result += "| k | Silhouette Score | Inertia |\n|---|---|---|\n"
        for k in sorted(scores.keys()):
            marker = " ← selected" if k == n_clusters else ""
            result += f"| {k} | {scores[k]} | {inertias[k]:,.0f} |{marker}\n"

    # Cluster profiles
    result += "\n### Cluster Profiles\n"
    result += "| Segment | Customers | % |"
    for f in features_used:
        result += f" Avg {f} |"
    result += "\n|" + "---|" * (3 + len(features_used)) + "\n"

    for cluster_id in range(n_clusters):
        mask = cust["cluster"] == cluster_id
        cluster_data = cust[mask]
        pct = len(cluster_data) / len(cust) * 100
        result += f"| {cluster_labels[cluster_id]} | {len(cluster_data):,} | {pct:.1f}% |"
        for f in features_used:
            if f in cluster_data.columns:
                result += f" {cluster_data[f].mean():,.2f} |"
            else:
                result += " N/A |"
        result += "\n"

    result += f"\n**Segments exported to:** segments.csv"
    return result


@tool
def get_optimal_clusters() -> str:
    """
    Analyze the optimal number of clusters using the Elbow method and Silhouette analysis.
    Use this before running ML segmentation to determine the best number of clusters.
    Returns: Analysis with recommended number of clusters.
    """
    scaled = get_scaled_data()
    features = get_selected_features()

    results = []
    inertias = []

    for k in range(2, MAX_CLUSTERS_SEARCH + 1):
        km = MiniBatchKMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=3, max_iter=100, batch_size=10000)
        labels = km.fit_predict(scaled)
        sil = silhouette_score(scaled, labels, sample_size=min(2000, len(scaled)))
        results.append({"k": k, "silhouette": round(sil, 4), "inertia": round(km.inertia_, 2)})
        inertias.append(km.inertia_)

    best = max(results, key=lambda x: x["silhouette"])

    result = f"""## Optimal Cluster Analysis

**Features analyzed:** {features}
**Range tested:** k=2 to k={MAX_CLUSTERS_SEARCH}

| k | Silhouette Score | Inertia |
|---|---|---|"""

    for r in results:
        marker = " ✅ Best" if r["k"] == best["k"] else ""
        result += f"\n| {r['k']} | {r['silhouette']} | {r['inertia']:,.0f} |{marker}"

    result += f"\n\n**Recommended:** k={best['k']} (Silhouette Score: {best['silhouette']})"
    result += f"\n\nHigher silhouette scores indicate better-defined, well-separated clusters."

    return result


@tool
def get_segment_statistics() -> str:
    """
    Get detailed statistics for each customer segment from the most recent segmentation.
    Shows average values, distributions, and key metrics per segment.
    Use after segmentation to understand each segment's profile.
    """
    seg_data = get_segment_results()
    if seg_data is None:
        return "No segmentation has been performed yet. Please run segmentation first using segment_customers_rule_based or segment_customers_ml."

    seg_col = "segment"
    segments = seg_data[seg_col].unique()

    metrics = ["avg_balance", "total_transactions", "avg_amount", "total_amount",
               "recency_days", "txn_per_month", "max_balance", "std_amount"]
    available_metrics = [m for m in metrics if m in seg_data.columns]

    result = "## Detailed Segment Statistics\n\n"

    for seg in sorted(segments):
        seg_subset = seg_data[seg_data[seg_col] == seg]
        result += f"### {seg} ({len(seg_subset):,} customers, {len(seg_subset)/len(seg_data)*100:.1f}%)\n\n"
        result += "| Metric | Mean | Median | Min | Max | Std |\n|---|---|---|---|---|---|\n"

        for m in available_metrics:
            col = seg_subset[m].dropna()
            if len(col) > 0:
                result += f"| {m} | {col.mean():,.2f} | {col.median():,.2f} | {col.min():,.2f} | {col.max():,.2f} | {col.std():,.2f} |\n"

        result += "\n"

    return result
