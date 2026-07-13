"""
Cross-check the Accra total-revenue figure using two independent methods.
Read-only on the cleaned data.

Usage:
    python scripts/verify_accra.py
"""

import os
import pandas as pd

CLEAN_PATH = os.path.join("clean", "retail_sales_clean.csv")

# ---- Load cleaned data (read-only) ----
df = pd.read_csv(CLEAN_PATH, parse_dates=["order_date"])

# ---- Method 1: groupby then select Accra ----
# Group every row by region, sum revenue within each group, then read the Accra cell.
method1 = df.groupby("region")["revenue ($)"].sum()["Accra"]

# ---- Method 2: boolean-filter to Accra rows, then sum ----
# Keep only rows where region == "Accra", then sum that column directly.
method2 = df.loc[df["region"] == "Accra", "revenue ($)"].sum()

# ---- Report both and confirm they agree ----
n_accra = int((df["region"] == "Accra").sum())
print("Accra order rows           :", n_accra)
print("Method 1 (groupby)         :", round(method1, 2))
print("Method 2 (filtered sum)    :", round(method2, 2))
print("Difference                 :", abs(method1 - method2))
# Use a tiny tolerance for floating-point; the two paths should be identical.
print("Match (within 1e-6)        :", abs(method1 - method2) < 1e-6)
