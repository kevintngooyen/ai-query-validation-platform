from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------
# Dashboard Configuration
# ---------------------------

st.set_page_config(
    page_title="AI Query Validation Platform",
    page_icon="���",
    layout="wide"
)

st.title("AI Query Validation Platform")

st.caption(
    "Evaluate AI-generated SQL against certified "
    "business questions and Snowflake results."
)


# ---------------------------
# File Paths
# ---------------------------

ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = ROOT / "evaluation" / "results"

BASELINE_FILE = (
    RESULTS_DIR / "baseline_50_results.csv"
)

IMPROVED_FILE = (
    RESULTS_DIR / "improved_50_results.csv"
)


# ---------------------------
# Load Evaluation Results
# ---------------------------

def load_results(path):
    if not path.exists():
        return None

    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp1252")

    df["status"] = (
        df["status"].astype(str).str.upper().str.strip()
    )

    return df


baseline = load_results(BASELINE_FILE)
improved = load_results(IMPROVED_FILE)

if baseline is None:
    st.error(
        "Baseline file not found. "
        "Run your evaluation and save "
        "baseline_50_corrected.csv first."
    )
    st.stop()


# ---------------------------
# Accuracy Calculations
# ---------------------------

def calculate_accuracy(df):
    if df is None or len(df) == 0:
        return 0.0

    return (
        df["status"].eq("PASS").sum()
        / len(df)
        * 100
    )


baseline_accuracy = calculate_accuracy(baseline)

if improved is not None:
    improved_accuracy = calculate_accuracy(improved)
else:
    improved_accuracy = None


# ---------------------------
# Summary Metrics
# ---------------------------

st.header("Evaluation Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Certified Questions",
    len(baseline)
)

col2.metric(
    "Baseline Accuracy",
    f"{baseline_accuracy:.1f}%"
)

if improved_accuracy is not None:

    improvement = (
        improved_accuracy - baseline_accuracy
    )

    col3.metric(
        "Improved Accuracy",
        f"{improved_accuracy:.1f}%"
    )

    col4.metric(
        "Accuracy Change",
        f"{improvement:+.1f} pp"
    )

else:
    col3.metric("Improved Accuracy", "N/A")
    col4.metric("Accuracy Change", "N/A")


# ---------------------------
# Accuracy Comparison Chart
# ---------------------------

st.header("Accuracy Comparison")

accuracy_data = pd.DataFrame({
    "Version": (
        ["Baseline", "Improved"]
        if improved_accuracy is not None
        else ["Baseline"]
    ),
    "Accuracy": (
        [baseline_accuracy, improved_accuracy]
        if improved_accuracy is not None
        else [baseline_accuracy]
    )
})

st.bar_chart(
    accuracy_data.set_index("Version"),
    y="Accuracy"
)


# ---------------------------
# Choose Evaluation Version
# ---------------------------

st.header("Failure Analysis")

versions = ["Baseline"]

if improved is not None:
    versions.append("Improved")

selected_version = st.selectbox(
    "Select evaluation version",
    versions
)

results = (
    baseline
    if selected_version == "Baseline"
    else improved
)

failed = results[
    results["status"] == "FAIL"
].copy()

passed = results[
    results["status"] == "PASS"
].copy()

col1, col2 = st.columns(2)

col1.metric("Passed Questions", len(passed))
col2.metric("Failed Questions", len(failed))


# ---------------------------
# Failure Categories
# ---------------------------

st.subheader("Failure Categories")

if "error_type" in failed.columns and not failed.empty:

    error_counts = (
        failed["error_type"]
        .fillna("UNKNOWN")
        .value_counts()
    )

    st.bar_chart(error_counts)

else:
    st.info("No failure categories available.")


# ---------------------------
# Detailed Evaluation Results
# ---------------------------

st.header("Certified Question Results")

status_filter = st.selectbox(
    "Filter by status",
    ["ALL", "PASS", "FAIL"]
)

filtered = results.copy()

if status_filter != "ALL":
    filtered = filtered[
        filtered["status"] == status_filter
    ]

display_columns = [
    col for col in [
        "question_id",
        "question",
        "status",
        "error_type"
    ]
    if col in filtered.columns
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True
)


# ---------------------------
# Individual Question Review
# ---------------------------

st.header("Question Inspector")

if not filtered.empty and "question_id" in filtered.columns:

    selected_question = st.selectbox(
        "Select a question ID",
        filtered["question_id"].tolist()
    )

    row = filtered[
        filtered["question_id"] == selected_question
    ].iloc[0]

    st.subheader("Business Question")
    st.write(row.get("question", ""))

    st.write("Status:", row["status"])
    st.write("Error Type:", row.get("error_type", ""))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Certified SQL")
        st.code(
            str(row.get("expected_sql", "")),
            language="sql"
        )

    with col2:
        st.subheader("AI-Generated SQL")
        st.code(
            str(row.get("generated_sql", "")),
            language="sql"
        )
