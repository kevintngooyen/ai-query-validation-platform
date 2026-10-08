from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = (
    PROJECT_ROOT
    / "evaluation"
    / "results"
)

baseline_file = (
    RESULTS_DIR
    / "baseline_results.csv"
)

improved_file = (
    RESULTS_DIR
    / "improved_results.csv"
)


baseline = pd.read_csv(baseline_file)
improved = pd.read_csv(improved_file)


def calculate_accuracy(df):
    return (
        df["status"]
        .eq("PASS")
        .mean()
    )


baseline_accuracy = calculate_accuracy(
    baseline
)

improved_accuracy = calculate_accuracy(
    improved
)

improvement = (
    improved_accuracy
    - baseline_accuracy
)


print()
print("=" * 50)
print("AI QUERY VALIDATION RESULTS")
print("=" * 50)

print()
print(
    f"Baseline Accuracy: "
    f"{baseline_accuracy:.1%}"
)

print(
    f"Improved Accuracy: "
    f"{improved_accuracy:.1%}"
)

print(
    f"Accuracy Improvement: "
    f"{improvement:.1%}"
)


# --------------------------------
# Baseline failure breakdown
# --------------------------------

baseline_failures = baseline[
    baseline["status"] == "FAIL"
]

if not baseline_failures.empty:

    print()
    print("Baseline Failure Types:")

    print(
        baseline_failures[
            "error_type"
        ]
        .value_counts()
    )


# --------------------------------
# Improved failure breakdown
# --------------------------------

improved_failures = improved[
    improved["status"] == "FAIL"
]

if not improved_failures.empty:

    print()
    print("Improved Failure Types:")

    print(
        improved_failures[
            "error_type"
        ]
        .value_counts()
    )


# --------------------------------
# Questions that improved
# --------------------------------

comparison = baseline[
    [
        "question_id",
        "question",
        "status"
    ]
].merge(
    improved[
        [
            "question_id",
            "status"
        ]
    ],
    on="question_id",
    suffixes=(
        "_baseline",
        "_improved"
    )
)

fixed_questions = comparison[
    (comparison["status_baseline"] == "FAIL")
    &
    (comparison["status_improved"] == "PASS")
]

print()
print("Questions Fixed After Improvements:")

if fixed_questions.empty:
    print("None")
else:
    for _, row in fixed_questions.iterrows():

        print(
            f'- {row["question"]}'
        )
