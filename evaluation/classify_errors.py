import re


def classify_error(
    question,
    expected_sql,
    generated_sql,
    execution_error=None
):
    """
    Classify why an AI-generated SQL query failed.
    """

    if execution_error:
        error_text = str(execution_error).lower()

        if "syntax" in error_text:
            return "INVALID_SQL"

        if "invalid identifier" in error_text:
            return "INVALID_COLUMN"

        if "does not exist" in error_text:
            return "INVALID_TABLE"

        return "EXECUTION_ERROR"

    expected = expected_sql.lower()
    generated = generated_sql.lower()
    question_text = question.lower()

    # -----------------------------
    # Metric errors
    # -----------------------------

    metrics = [
        "gross_revenue",
        "total_payments",
        "outstanding_amount",
        "order_count",
        "average_order_value",
        "payment_rate",
    ]

    expected_metrics = [
        metric
        for metric in metrics
        if metric in expected
    ]

    generated_metrics = [
        metric
        for metric in metrics
        if metric in generated
    ]

    if set(expected_metrics) != set(generated_metrics):
        return "WRONG_METRIC"

    # -----------------------------
    # Aggregation errors
    # -----------------------------

    aggregations = [
        "sum(",
        "avg(",
        "count(",
        "min(",
        "max(",
    ]

    expected_aggs = [
        agg
        for agg in aggregations
        if agg in expected
    ]

    generated_aggs = [
        agg
        for agg in aggregations
        if agg in generated
    ]

    if set(expected_aggs) != set(generated_aggs):
        return "WRONG_AGGREGATION"

    # -----------------------------
    # Grouping errors
    # -----------------------------

    expected_group = "group by" in expected
    generated_group = "group by" in generated

    if expected_group != generated_group:
        return "WRONG_GROUPING"

    # -----------------------------
    # Filter errors
    # -----------------------------

    expected_where = "where" in expected
    generated_where = "where" in generated

    if expected_where != generated_where:
        return "WRONG_FILTER"

    # -----------------------------
    # Limit errors
    # -----------------------------

    expected_limit = re.search(r"limit\s+\d+", expected)
    generated_limit = re.search(r"limit\s+\d+", generated)

    if bool(expected_limit) != bool(generated_limit):
        return "WRONG_LIMIT"

    # -----------------------------
    # Ordering errors
    # -----------------------------

    expected_order = "order by" in expected
    generated_order = "order by" in generated

    if expected_order != generated_order:
        return "WRONG_ORDERING"

    # -----------------------------
    # Ambiguous terminology
    # -----------------------------

    ambiguous_terms = [
        "best",
        "top",
        "revenue",
        "performance",
        "highest",
    ]

    if any(
        term in question_text
        for term in ambiguous_terms
    ):
        return "AMBIGUOUS_TERM"

    return "RESULT_MISMATCH"
