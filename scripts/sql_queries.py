"""
Run three analytical SQL queries against retail.db (table: sales).
Prints each query's result. The SQL lives here so it is rerunnable/verifiable.

Usage:
    python scripts/sql_queries.py
"""

import sqlite3

DB_PATH = "retail.db"

# ---------------------------------------------------------------------------
# Q1. Revenue by region x category (pivot-style).
# SQLite has no PIVOT, so we pivot with conditional aggregation:
# one SUM(CASE WHEN category = X ...) column per category.
# ---------------------------------------------------------------------------
Q1 = """
SELECT
    region,
    ROUND(SUM(CASE WHEN category = 'Beauty'      THEN "revenue ($)" END), 2) AS beauty,
    ROUND(SUM(CASE WHEN category = 'Clothing'    THEN "revenue ($)" END), 2) AS clothing,
    ROUND(SUM(CASE WHEN category = 'Electronics' THEN "revenue ($)" END), 2) AS electronics,
    ROUND(SUM(CASE WHEN category = 'Groceries'   THEN "revenue ($)" END), 2) AS groceries,
    ROUND(SUM(CASE WHEN category = 'Home'        THEN "revenue ($)" END), 2) AS home,
    ROUND(SUM("revenue ($)"), 2) AS total
FROM sales
GROUP BY region
ORDER BY total DESC;
"""

# ---------------------------------------------------------------------------
# Q2. Month-over-month revenue growth %.
# First aggregate revenue per calendar month, then use the LAG window function
# to read the previous month's revenue on the same row and compute growth.
# ---------------------------------------------------------------------------
Q2 = """
WITH monthly AS (
    SELECT
        strftime('%Y-%m', order_date) AS month,
        SUM("revenue ($)")            AS revenue
    FROM sales
    GROUP BY month
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS prev_month_revenue,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month))
        * 100.0 / LAG(revenue) OVER (ORDER BY month),
        2
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;
"""

# ---------------------------------------------------------------------------
# Q3. Customers who ordered in 3+ distinct categories.
# COUNT(DISTINCT category) per customer, keep those with >= 3.
# ---------------------------------------------------------------------------
Q3 = """
SELECT
    customer_id,
    COUNT(DISTINCT category)   AS distinct_categories,
    COUNT(*)                   AS orders,
    ROUND(SUM("revenue ($)"), 2) AS total_revenue
FROM sales
GROUP BY customer_id
HAVING COUNT(DISTINCT category) >= 3
ORDER BY distinct_categories DESC, total_revenue DESC;
"""


# ---------------------------------------------------------------------------
# Q4. Top 5 regions by average order value.
# An order can span several line-item rows, so first sum revenue per order
# (region, order_id), then average those per-order totals within each region.
# ---------------------------------------------------------------------------
Q4 = """
SELECT
    region,
    ROUND(AVG(order_revenue), 2) AS avg_order_value,
    COUNT(*)                     AS num_orders
FROM (
    SELECT region, order_id, SUM("revenue ($)") AS order_revenue
    FROM sales
    GROUP BY region, order_id
)
GROUP BY region
ORDER BY avg_order_value DESC
LIMIT 5;
"""


def run(conn, title, sql, limit=None):
    cur = conn.cursor()
    rows = cur.execute(sql).fetchall()
    cols = [d[0] for d in cur.description]
    print(f"\n=== {title} ===")
    print(" | ".join(cols))
    for r in (rows if limit is None else rows[:limit]):
        print(" | ".join("" if v is None else str(v) for v in r))
    return rows


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        run(conn, "Q1: Revenue by region x category (pivot)", Q1)
        run(conn, "Q2: Month-over-month revenue growth %", Q2)
        q3 = run(conn, "Q3: Customers in 3+ categories (top 15 shown)", Q3, limit=15)
        # Summary counts for Q3.
        four_plus = sum(1 for r in q3 if r[1] >= 4)
        five = sum(1 for r in q3 if r[1] == 5)
        print(f"\nQ3 summary: {len(q3)} customers ordered in 3+ categories; "
              f"{four_plus} in 4+, {five} in all 5.")
        run(conn, "Q4: Top 5 regions by average order value", Q4)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
