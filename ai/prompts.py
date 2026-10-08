from semantic_context import BUSINESS_METRICS, TABLE_CONTEXT


def build_sql_prompt(question):

    metrics_text = ""

    for metric_name, metric_info in BUSINESS_METRICS.items():

        metrics_text += f"""
Metric: {metric_name}
Definition: {metric_info["definition"]}
Formula: {metric_info["formula"]}
"""

    prompt = f"""
You are a data analyst generating Snowflake SQL.

Use only the following table:

{TABLE_CONTEXT}

Business metric definitions:

{metrics_text}

Rules:

1. Generate valid Snowflake SQL.

2. Use only:
AI_QUERY_VALIDATION.DBT_DEV.MART_BUSINESS_METRICS

3. Do not invent tables or columns.

4. Follow the business metric definitions exactly.

5. If the user asks for "revenue",
use gross_revenue.

6. If the user asks for overall payment rate, use:

SUM(total_payments) /
NULLIF(SUM(gross_revenue), 0)

7. If the user asks for overall average order value, use:

SUM(gross_revenue) /
NULLIF(SUM(order_count), 0)

8. If the user asks for the highest or most,
use ORDER BY DESC and LIMIT 1.

9. If the user asks for the lowest or least,
use ORDER BY ASC and LIMIT 1.

10. Return SQL only.

11. Do not include markdown.

12. Do not explain the query.

Business question:

{question}
"""

    return prompt