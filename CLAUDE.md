# CLAUDE.md

Guidance for Claude Code when working in this project.

## About this project

Data analysis work for a data analyst. The primary dataset is retail sales data
for 2025 (`retail_sales_2025.csv` / `.xlsx`) with columns: `order_id`,
`order_date`, `region`, `category`, `quantity`, `unit_price ($)`, `customer_id`,
`revenue ($)`. Note: some rows contain negative quantity/revenue (returns).

## Working rules

1. **Language & tools** — Use Python with pandas for all analysis. Prefer pandas
   idioms over manual loops.

2. **Preview after loading** — After loading any dataset, always show a preview:
   `df.head()`, `df.shape`, and `df.dtypes`. Do this before any analysis.

3. **Never modify raw data** — Treat the source files (`retail_sales_2025.csv`,
   `retail_sales_2025.xlsx`) as read-only. Write any cleaned or transformed data
   to a `clean/` folder (e.g. `clean/retail_sales_2025_clean.csv`). Never
   overwrite the originals.

4. **Comment all code** — Add plain-language comments explaining each step, so the
   code is easy to follow without prior context.

5. **Preserve the code behind the numbers** — Whenever you report a computed
   number, table, or statistic, the code that produced it must be saved as a
   runnable script in `scripts/` so results can be independently verified and
   rerun. Do **not** paste that code inline in the chat — just reference the
   script path (e.g. `scripts/quality_report.py`).
