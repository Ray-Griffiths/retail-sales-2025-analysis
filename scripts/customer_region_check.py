"""
Check whether customer_id maps to a single region in the retail data.

This backs a claim used when advising on lookup formulas: a lookup by customer_id
can only ever return the FIRST matching region, so it is only meaningful if each
customer has exactly one region. This script quantifies how often that holds.

Input:  clean/retail_sales_2025_clean.csv
Usage:  python scripts/customer_region_check.py
"""

import pandas as pd

df = pd.read_csv("clean/retail_sales_2025_clean.csv")

# Number of distinct regions each customer appears in.
regions_per_customer = df.groupby("customer_id")["region"].nunique()

n_customers = int(regions_per_customer.size)
n_multi = int((regions_per_customer > 1).sum())          # customers spanning >1 region

print(f"distinct customers:            {n_customers}")
print(f"customers in >1 region:        {n_multi} "
      f"({n_multi / n_customers:.0%})")
print(f"customers with a single region:{n_customers - n_multi}")

# Concrete example for documentation.
example = df["customer_id"].iloc[0]
regs = sorted(df.loc[df["customer_id"] == example, "region"].unique())
print(f"example customer {example} regions: {regs}")
