"""
Top customers and revenue concentration analysis on clean/retail_sales_clean.csv.
Read-only.

Usage:
    python scripts/customer_concentration.py
"""

import os
import pandas as pd

CLEAN_PATH = os.path.join("clean", "retail_sales_clean.csv")

# ---- Load cleaned data (read-only) ----
df = pd.read_csv(CLEAN_PATH, parse_dates=["order_date"])

# Total revenue across all customers (denominator for every share below).
total_revenue = df["revenue ($)"].sum()

# ---- Revenue per customer ----
# Sum revenue for every customer_id, largest spenders first.
cust_rev = df.groupby("customer_id")["revenue ($)"].sum().sort_values(ascending=False)
n_customers = len(cust_rev)

# ---- Top 10 customers ----
top10 = cust_rev.head(10).copy()
top10_share = top10.sum() / total_revenue * 100

print("=== TOP 10 CUSTOMERS BY REVENUE ===")
for cid, rev in top10.items():
    print(f"customer {cid}: ${rev:,.2f}  ({rev/total_revenue*100:.2f}% of total)")
print(f"\nTop 10 customers combined: ${top10.sum():,.2f}  ({top10_share:.2f}% of total)")

# ---- Concentration: share held by the TOP 10% of customers ----
# Number of customers that make up the top decile (round to nearest whole customer).
top_decile_n = round(n_customers * 0.10)
top_decile_rev = cust_rev.head(top_decile_n).sum()
top_decile_share = top_decile_rev / total_revenue * 100

print("\n=== CONCENTRATION ===")
print(f"Total customers            : {n_customers}")
print(f"Total revenue              : ${total_revenue:,.2f}")
print(f"Top 10% = top {top_decile_n} customers")
print(f"Their revenue              : ${top_decile_rev:,.2f}")
print(f"Share of total revenue     : {top_decile_share:.2f}%")

# ---- Extra context: how far from an even split? ----
# If revenue were perfectly evenly spread, the top 10% would hold exactly 10%.
even_share = 10.0
print(f"\nEven-split benchmark       : {even_share:.1f}%  (top 10% would hold 10% if flat)")
print(f"Top 20% share              : {cust_rev.head(round(n_customers*0.20)).sum()/total_revenue*100:.2f}%")
print(f"Top 50% share              : {cust_rev.head(round(n_customers*0.50)).sum()/total_revenue*100:.2f}%")
