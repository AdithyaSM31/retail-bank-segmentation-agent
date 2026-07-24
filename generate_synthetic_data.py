"""
Generate synthetic product holdings data for the recommendation engine.
Maps customers to banking product ownership (credit cards, loans, investments).
"""
import pandas as pd
import numpy as np
from data_loader import load_raw_data

def generate_synthetic_products(output_path: str):
    """Generate synthetic product holdings for all unique customers."""
    df = load_raw_data()
    customers = df[["CustomerID", "CustAccountBalance"]].drop_duplicates("CustomerID")
    
    np.random.seed(42)
    n = len(customers)
    
    # Product ownership probabilities vary by balance tier
    balances = customers["CustAccountBalance"].values
    median_bal = np.nanmedian(balances)
    p75_bal = np.nanpercentile(balances, 75)
    
    high_bal = balances > p75_bal
    mid_bal = (balances > median_bal) & (balances <= p75_bal)
    low_bal = balances <= median_bal
    
    # Credit Card
    cc_prob = np.where(high_bal, 0.85, np.where(mid_bal, 0.55, 0.25))
    has_credit_card = np.random.random(n) < cc_prob
    
    # Personal Loan
    loan_prob = np.where(high_bal, 0.30, np.where(mid_bal, 0.45, 0.35))
    has_personal_loan = np.random.random(n) < loan_prob
    
    # Fixed Deposit
    fd_prob = np.where(high_bal, 0.70, np.where(mid_bal, 0.40, 0.15))
    has_fixed_deposit = np.random.random(n) < fd_prob
    
    # Mutual Funds / SIP
    mf_prob = np.where(high_bal, 0.60, np.where(mid_bal, 0.25, 0.08))
    has_mutual_funds = np.random.random(n) < mf_prob
    
    # Insurance
    ins_prob = np.where(high_bal, 0.55, np.where(mid_bal, 0.35, 0.20))
    has_insurance = np.random.random(n) < ins_prob
    
    # Mobile Banking
    mobile_prob = np.where(high_bal, 0.90, np.where(mid_bal, 0.75, 0.50))
    has_mobile_banking = np.random.random(n) < mobile_prob
    
    products = pd.DataFrame({
        "CustomerID": customers["CustomerID"].values,
        "has_credit_card": has_credit_card.astype(int),
        "has_personal_loan": has_personal_loan.astype(int),
        "has_fixed_deposit": has_fixed_deposit.astype(int),
        "has_mutual_funds": has_mutual_funds.astype(int),
        "has_insurance": has_insurance.astype(int),
        "has_mobile_banking": has_mobile_banking.astype(int),
    })
    
    # Total products held
    products["total_products"] = products.iloc[:, 1:].sum(axis=1)
    
    products.to_csv(output_path, index=False)
    print(f"Synthetic products generated: {len(products):,} customers, saved to {output_path}")
    
    # Summary
    print("\nProduct Penetration:")
    for col in products.columns[1:-1]:
        pct = products[col].mean() * 100
        print(f"  {col}: {pct:.1f}%")
    print(f"  Avg products per customer: {products['total_products'].mean():.2f}")

    return products


if __name__ == "__main__":
    from config import SYNTHETIC_PRODUCTS_CSV
    generate_synthetic_products(str(SYNTHETIC_PRODUCTS_CSV))
