"""
Feature Engineering Tool — Derives, selects, and scales customer-level features
for use in segmentation and analysis.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from langchain_core.tools import tool
from data_loader import get_customer_features, load_raw_data

# Module-level cache for scaled data
_scaled_data = None
_selected_features = None


@tool
def engineer_customer_features() -> str:
    """
    Aggregate raw transaction data into customer-level features suitable for segmentation.
    Creates features like: total_transactions, total_amount, avg_amount, avg_balance,
    max_balance, recency_days, tenure_days, txn_per_month, std_amount, age, and more.
    Use this as the first step before any segmentation or analysis.
    Returns a summary of the engineered features.
    """
    cust = get_customer_features(force_reload=True)

    result = f"Customer Feature Engineering Complete. Processed {len(cust)} customers."
    return result


@tool
def select_features_for_segmentation(feature_list: str) -> str:
    """
    Select specific features from the customer feature set for use in segmentation.
    The selected features will be cached and used by the segmentation tool.
    Args:
        feature_list: Comma-separated list of feature names to select.
            Available features: total_transactions, total_amount, avg_amount, max_amount,
            std_amount, avg_balance, max_balance, min_balance, recency_days, tenure_days,
            txn_per_month, balance_to_avg_txn, age
    Returns: Confirmation with summary statistics of selected features.
    """
    global _selected_features
    cust = get_customer_features()
    features = [f.strip() for f in feature_list.split(",")]

    invalid = [f for f in features if f not in cust.columns]
    if invalid:
        return f"Invalid features: {invalid}. Available numeric features: {[c for c in cust.select_dtypes(include=[np.number]).columns.tolist()]}"

    _selected_features = features
    subset = cust[features].describe().round(2).to_string()

    return f"""## Features Selected for Segmentation

**Selected:** {features}

### Summary Statistics
{subset}

These features are now cached and will be used by the segmentation tool. 
Call the segmentation tool next to cluster customers based on these features.
"""


@tool
def scale_features(method: str = "standard") -> str:
    """
    Scale the selected features for ML-based segmentation.
    Scaling is required before running KMeans or similar distance-based clustering.
    Args:
        method: Scaling method — 'standard' (StandardScaler, zero mean unit variance) 
                or 'minmax' (MinMaxScaler, scales to 0-1 range). Default is 'standard'.
    Returns: Confirmation with scaled feature statistics.
    """
    global _scaled_data, _selected_features
    cust = get_customer_features()

    if _selected_features is None:
        # Default features if none selected
        _selected_features = ["avg_balance", "total_transactions", "avg_amount", "recency_days", "txn_per_month"]

    features = _selected_features
    data = cust[features].fillna(0)

    if method == "minmax":
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()

    scaled = scaler.fit_transform(data)
    _scaled_data = pd.DataFrame(scaled, columns=features, index=cust.index)

    result = f"""## Feature Scaling Complete

**Method:** {'StandardScaler (zero mean, unit variance)' if method == 'standard' else 'MinMaxScaler (0-1 range)'}
**Features scaled:** {features}
**Samples:** {len(_scaled_data):,}

### Post-Scaling Statistics
{_scaled_data.describe().round(4).to_string()}
"""
    return result


def get_scaled_data() -> pd.DataFrame:
    """Get the cached scaled data (used internally by segmentation tool)."""
    global _scaled_data, _selected_features
    if _scaled_data is not None:
        return _scaled_data.copy()

    # Auto-scale with defaults if not done yet
    cust = get_customer_features()
    if _selected_features is None:
        _selected_features = ["avg_balance", "total_transactions", "avg_amount", "recency_days", "txn_per_month"]

    data = cust[_selected_features].fillna(0)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(data)
    _scaled_data = pd.DataFrame(scaled, columns=_selected_features, index=cust.index)
    return _scaled_data.copy()


def get_selected_features() -> list:
    """Get the currently selected feature list."""
    global _selected_features
    if _selected_features is None:
        _selected_features = ["avg_balance", "total_transactions", "avg_amount", "recency_days", "txn_per_month"]
    return _selected_features
