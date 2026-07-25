"""
Data loader and preprocessing pipeline.
Handles ingestion, cleaning, and preparation of the bank transactions dataset.
"""
import pandas as pd
import numpy as np
from datetime import datetime
from config import TRANSACTIONS_CSV, SYNTHETIC_PRODUCTS_CSV

_raw_data = None
_customer_features = None


def load_raw_data(force_reload: bool = False) -> pd.DataFrame:
    """Load and clean the raw bank transactions CSV."""
    global _raw_data
    if _raw_data is not None and not force_reload:
        return _raw_data.copy()

    df = pd.read_csv(TRANSACTIONS_CSV)

    # --- Clean column names ---
    df.columns = df.columns.str.strip()
    df.rename(columns={"TransactionAmount (INR)": "TransactionAmount"}, inplace=True)

    # --- Parse dates ---
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], format="%d/%m/%y", errors="coerce")

    # --- Parse DOB and compute age ---
    df["CustomerDOB"] = pd.to_datetime(df["CustomerDOB"], format="%d/%m/%y", errors="coerce")
    # Filter out obviously invalid DOBs (year < 1920 or > 2010)
    invalid_dob_mask = (df["CustomerDOB"].dt.year < 1920) | (df["CustomerDOB"].dt.year > 2010)
    df.loc[invalid_dob_mask, "CustomerDOB"] = pd.NaT

    # --- Clean gender ---
    df["CustGender"] = df["CustGender"].str.strip().str.upper().map({"M": "Male", "F": "Female"})

    # --- Clean location ---
    df["CustLocation"] = df["CustLocation"].str.strip().str.title()

    # --- Clean numeric columns ---
    df["CustAccountBalance"] = pd.to_numeric(df["CustAccountBalance"], errors="coerce")
    df["TransactionAmount"] = pd.to_numeric(df["TransactionAmount"], errors="coerce")

    # --- Drop rows with missing critical fields ---
    df.dropna(subset=["CustomerID", "TransactionAmount"], inplace=True)

    _raw_data = df
    return _raw_data.copy()


def get_customer_features(force_reload: bool = False) -> pd.DataFrame:
    """
    Aggregate transaction-level data to customer-level features.
    This is the primary feature-engineered dataset used for segmentation.
    """
    global _customer_features
    if _customer_features is not None and not force_reload:
        return _customer_features.copy()

    df = load_raw_data(force_reload)
    ref_date = df["TransactionDate"].max()

    agg = df.groupby("CustomerID").agg(
        total_transactions=("TransactionID", "count"),
        total_amount=("TransactionAmount", "sum"),
        avg_amount=("TransactionAmount", "mean"),
        max_amount=("TransactionAmount", "max"),
        min_amount=("TransactionAmount", "min"),
        std_amount=("TransactionAmount", "std"),
        avg_balance=("CustAccountBalance", "mean"),
        max_balance=("CustAccountBalance", "max"),
        min_balance=("CustAccountBalance", "min"),
        last_transaction_date=("TransactionDate", "max"),
        first_transaction_date=("TransactionDate", "min"),
        gender=("CustGender", "first"),
        location=("CustLocation", "first"),
        dob=("CustomerDOB", "first"),
    ).reset_index()

    # --- Derived features ---
    agg["recency_days"] = (ref_date - agg["last_transaction_date"]).dt.days
    agg["tenure_days"] = (agg["last_transaction_date"] - agg["first_transaction_date"]).dt.days
    agg["std_amount"] = agg["std_amount"].fillna(0)

    # Age from DOB
    agg["age"] = ((ref_date - agg["dob"]).dt.days / 365.25).round(0)
    invalid_age = (agg["age"] < 10) | (agg["age"] > 100)
    agg.loc[invalid_age, "age"] = np.nan

    # Transaction frequency per month (approx)
    agg["months_active"] = (agg["tenure_days"] / 30).clip(lower=1)
    agg["txn_per_month"] = (agg["total_transactions"] / agg["months_active"]).round(2)

    # Balance-to-transaction ratio
    agg["balance_to_avg_txn"] = (agg["avg_balance"] / agg["avg_amount"].replace(0, np.nan)).round(2)

    _customer_features = agg
    return _customer_features.copy()


def load_synthetic_products() -> pd.DataFrame:
    """Load synthetic product holdings data."""
    try:
        return pd.read_csv(SYNTHETIC_PRODUCTS_CSV)
    except FileNotFoundError:
        return pd.DataFrame()


def get_data_summary() -> dict:
    """Return a quick summary of the loaded dataset."""
    df = load_raw_data()
    return {
        "total_transactions": len(df),
        "unique_customers": df["CustomerID"].nunique(),
        "date_range": f"{df['TransactionDate'].min()} to {df['TransactionDate'].max()}",
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "shape": df.shape,
    }


def reset_cache():
    """Reset all cached data."""
    global _raw_data, _customer_features
    _raw_data = None
    _customer_features = None
