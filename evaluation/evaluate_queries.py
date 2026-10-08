import os
import sys
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI_DIR = PROJECT_ROOT / "ai"

sys.path.append(str(AI_DIR))

from generate_sql import generate_sql
from classify_errors import classify_error


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# Snowflake connection
# --------------------------------------------------

def get_connection():

    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        private_key_file=os.getenv(
            "SNOWFLAKE_PRIVATE_KEY_PATH"
        ),
        warehouse=os.getenv(
            "SNOWFLAKE_WAREHOUSE"
        ),
        database=os.getenv(
            "SNOWFLAKE_DATABASE"
        ),
        schema="DBT_DEV",
    )


# --------------------------------------------------
# Run SQL query
# --------------------------------------------------

def run_query(conn, sql):

    cursor = conn.cursor()

    try:
        cursor.execute(sql)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        return pd.DataFrame(
            rows,
            columns=columns
        )

    finally:
        cursor.close()


# --------------------------------------------------
# Normalize query results
# --------------------------------------------------

def normalize_dataframe(df):

    df = df.copy()

    # Standardize column names
    df.columns = [
        str(column).lower()
        for column in df.columns
    ]

    # Sort columns alphabetically
    df = df.reindex(
        sorted(df.columns),
        axis=1
    )

    # Sort rows so ordering differences
    # do not automatically cause failures
    if not df.empty and len(df.columns) > 0:

        try:
            df = (
                df
                .sort_values(
                    by=list(df.columns)
                )
                .reset_index(drop=True)
            )

        except TypeError:
            # Some mixed data types may not sort cleanly
            df = df.reset_index(drop=True)

    return df


# --------------------------------------------------
# Compare expected vs AI results
# --------------------------------------------------

def compare_results(expected, actual):

    expected = normalize_dataframe(expected)
    actual = normalize_dataframe(actual)

    try:

        pd.testing.assert_frame_equal(
            expected,
            actual,
            check_dtype=False,
            check_exact=False,
            rtol=1e-5,
            atol=1e-5
        )

        return True

    except AssertionError:
        return False


# --------------------------------------------------
# Main evaluation
# --------------------------------------------------

def main():

    questions_path = (
        PROJECT_ROOT
        / "evaluation"
        / "certified_questions.csv"
    )

    questions = pd.read_csv(
        questions_path
    )

    print(
        f"Loaded {len(questions)} certified questions."
    )

    conn = get_connection()

    results = []

    try:

        for _, row in questions.iterrows():

            question_id = row["question_id"]
            question = row["question"]
            expected_sql = row["expected_sql"]

            # Important:
            # reset for every question
            generated_sql = ""

            print()
            print("=" * 60)
            print(
                f"Question {question_id}"
            )
            print("=" * 60)

            print(question)

            try:

                # ----------------------------------
                # Run certified SQL
                # ----------------------------------

                expected_result = run_query(
                    conn,
                    expected_sql
                )

                # ----------------------------------
                # Ask AI to generate SQL
                # ----------------------------------

                generated_sql = generate_sql(
                    question
                )

                print()
                print("Generated SQL:")
                print(generated_sql)

                # ----------------------------------
                # Run AI-generated SQL
                # ----------------------------------

                actual_result = run_query(
                    conn,
                    generated_sql
                )

                # ----------------------------------
                # Compare results
                # ----------------------------------

                passed = compare_results(
                    expected_result,
                    actual_result
                )

                if passed:

                    status = "PASS"
                    error_type = ""

                else:

                    status = "FAIL"

                    error_type = classify_error(
                        question=question,
                        expected_sql=expected_sql,
                        generated_sql=generated_sql
                    )

                print()
                print(
                    f"Status: {status}"
                )

                if error_type:

                    print(
                        f"Error Type: {error_type}"
                    )

            except Exception as error:

                status = "FAIL"

                error_type = classify_error(
                    question=question,
                    expected_sql=expected_sql,
                    generated_sql=generated_sql,
                    execution_error=error
                )

                print()
                print("Status: FAIL")

                print(
                    f"Error Type: {error_type}"
                )

                print(
                    f"Error Message: {error}"
                )

            # --------------------------------------
            # Save evaluation result
            # --------------------------------------

            results.append({
                "question_id": question_id,
                "question": question,
                "expected_sql": expected_sql,
                "generated_sql": generated_sql,
                "status": status,
                "error_type": error_type
            })

    finally:

        conn.close()


    # --------------------------------------------------
    # Save evaluation results
    # --------------------------------------------------

    results_df = pd.DataFrame(
        results
    )

    output_dir = (
        PROJECT_ROOT
        / "evaluation"
        / "results"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir
        / "evaluation_results.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )


    # --------------------------------------------------
    # Calculate accuracy
    # --------------------------------------------------

    total_count = len(
        results_df
    )

    passed_count = (
        results_df["status"]
        .eq("PASS")
        .sum()
    )

    failed_count = (
        total_count
        - passed_count
    )

    accuracy = (
        passed_count / total_count
        if total_count > 0
        else 0
    )


    # --------------------------------------------------
    # Print summary
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)

    print(
        f"Total Questions: {total_count}"
    )

    print(
        f"Passed: {passed_count}"
    )

    print(
        f"Failed: {failed_count}"
    )

    print(
        f"Accuracy: {accuracy:.1%}"
    )


    # --------------------------------------------------
    # Error breakdown
    # --------------------------------------------------

    failed_results = results_df[
        results_df["status"] == "FAIL"
    ]

    if not failed_results.empty:

        print()
        print("Failure Breakdown:")
        print("-" * 30)

        error_counts = (
            failed_results[
                "error_type"
            ]
            .value_counts()
        )

        for error_type, count in error_counts.items():

            print(
                f"{error_type}: {count}"
            )


    print()
    print(
        f"Results saved to:"
    )

    print(
        output_file
    )


# --------------------------------------------------
# Run program
# --------------------------------------------------

if __name__ == "__main__":
    main()
