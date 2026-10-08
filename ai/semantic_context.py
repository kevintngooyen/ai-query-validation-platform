BUSINESS_METRICS = {
    "gross_revenue": {
        "definition": "Total value of customer orders before payments, refunds, or adjustments.",
        "formula": "SUM(gross_revenue)",
        "rules": [
            "Use gross_revenue when the user asks for revenue unless another revenue metric is explicitly requested."
        ]
    },

    "total_payments": {
        "definition": "Total amount received from customers.",
        "formula": "SUM(total_payments)",
        "rules": [
            "Do not treat total_payments as gross revenue."
        ]
    },

    "outstanding_amount": {
        "definition": "Amount customers still owe after payments.",
        "formula": "SUM(outstanding_amount)",
        "rules": [
            "Use outstanding_amount when the question asks about unpaid balances or money still owed."
        ]
    },

    "order_count": {
        "definition": "Number of unique customer orders.",
        "formula": "SUM(order_count)",
        "rules": [
            "Use order_count when comparing number of orders."
        ]
    },

    "average_order_value": {
        "definition": "Overall gross revenue divided by total number of orders.",
        "formula": "SUM(gross_revenue) / NULLIF(SUM(order_count), 0)",
        "rules": [
            "Do not calculate overall average order value using AVG(average_order_value)."
        ]
    },

    "payment_rate": {
        "definition": "Total payments divided by gross revenue.",
        "formula": (
            "SUM(total_payments) / "
            "NULLIF(SUM(gross_revenue), 0)"
        ),
        "rules": [
            "Never use AVG(payment_rate) for an overall rate.",
            "Always calculate rates using aggregated totals."
    ]
    },
}


TABLE_CONTEXT = """
Table:
AI_QUERY_VALIDATION.DBT_DEV.MART_BUSINESS_METRICS

Columns:

customer_id
- Unique identifier for a customer.

customer_name
- Customer name.

region
- Customer geographic region.

segment
- Customer segment.

product_id
- Unique identifier for a product.

product_name
- Product name.

category
- Product category.

order_count
- Number of unique orders for the customer/product grouping.

gross_revenue
- Total value of orders before payments or adjustments.

total_payments
- Total customer payments received.

outstanding_amount
- Gross revenue that remains unpaid.

average_order_value
- Gross revenue divided by number of orders.

payment_rate
- Total payments divided by gross revenue.


Important SQL rules:

1. Use only MART_BUSINESS_METRICS.
2. Use gross_revenue when a question simply asks for "revenue."
3. For overall payment rate use:
   SUM(total_payments) / NULLIF(SUM(gross_revenue), 0)

4. For overall average order value use:
   SUM(gross_revenue) / NULLIF(SUM(order_count), 0)

5. When comparing customers, group by customer_name.

6. When comparing products, group by product_name.

7. When comparing regions, group by region.

8. When comparing segments, group by segment.

9. When comparing product categories, group by category.

10. Questions asking for "highest" or "most" normally require:
    ORDER BY the requested metric DESC
    LIMIT 1
"""