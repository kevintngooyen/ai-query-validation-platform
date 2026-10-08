from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_FILE = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
    / "improved_50_results.csv"
)

# Load results
df = pd.read_csv(RESULTS_FILE)

# Separate passing and failing questions
passed = df[df["status"] == "PASS"]
failed = df[df["status"] == "FAIL"]

# Calculate accuracy
total = len(df)
accuracy = len(passed) / total if total else 0

print("=" * 50)
print("AI QUERY FAILURE ANALYSIS")
print("=" * 50)

print(f"Total Questions: {total}")
print(f"Passed: {len(passed)}")
print(f"Failed: {len(failed)}")
print(f"Accuracy: {accuracy:.1%}")

# Failure categories
print("\nFailure Categories:")

print(
    failed["error_type"].value_counts(
        dropna=False
    )
)

# Display failed questions
print("\nFailed Questions:")

for _, row in failed.iterrows():

    print(f"\nQuestion {row['question_id']}")
    print(row["question"])
    print(f"Error: {row['error_type']}")

# Detailed examples
print("\nDetailed SQL Comparison:")

for _, row in failed.head(5).iterrows():

    print("\n" + "-" * 50)

    print("Question:")
    print(row["question"])

    print("\nExpected SQL:")
    print(row["expected_sql"])

    print("\nAI-Generated SQL:")
    print(row["generated_sql"])

    print("\nError Type:")
    print(row["error_type"])
