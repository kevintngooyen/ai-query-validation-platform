from pathlib import Path

import pandas as pd
import streamlit as st

from certification import (
    init_db,
    save_review,
    get_review
)

from certification import sql_hash as sql_hash_for_form

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

# ---------------------------
# Select Results for Review
# ---------------------------

st.header("Evaluation Results")

if improved is not None:
    results = improved
    selected_version = "Improved"
    st.success("Using improved_50_results.csv")
else:
    results = baseline
    selected_version = "Baseline"
    st.warning(
        "Improved results not found. Using baseline instead."
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

# ---------------------------
# Business Question Certification
# ---------------------------

st.header("Business Question Certification")

init_db()

st.write(
    "Review AI-generated SQL and approve or reject "
    "queries based on business logic and correctness."
)

if results.empty:
    st.info("No evaluation questions available.")

else:
    # Select question
    question_ids = results["question_id"].tolist()

    review_question_id = st.selectbox(
        "Select a question to certify",
        question_ids,
        key="certification_question"
    )

    review_row = results[
        results["question_id"] == review_question_id
    ].iloc[0]

    question = str(review_row["question"])

    generated_sql = str(
        review_row.get("generated_sql", "")
    )

    expected_sql = str(
        review_row.get("expected_sql", "")
    )

    evaluation_status = str(
        review_row["status"]
    ).upper()

    # Load existing review
    existing_review = get_review(
        selected_version,
        review_question_id,
        generated_sql
    )

    certification_status = (
        existing_review["decision"]
        if existing_review
        else "PENDING"
    )

    # Display question
    st.subheader("Business Question")
    st.write(question)

    col1, col2 = st.columns(2)

    with col1:
        st.write("Automated Evaluation")
        st.write(evaluation_status)

    with col2:
        st.write("Certification Status")
        st.write(certification_status)

    # SQL comparison
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Certified SQL")
        st.code(expected_sql, language="sql")

    with col2:
        st.subheader("AI-Generated SQL")
        st.code(generated_sql, language="sql")

    # Existing reviewer information
    if existing_review:
        st.caption(
            f"Previously reviewed by "
            f"{existing_review['reviewer']} "
            f"at {existing_review['reviewed_at']}"
        )

    # Unique form for each query and version
    form_key = (
        f"review_{selected_version}_"
        f"{review_question_id}_"
        f"{sql_hash_for_form(generated_sql)}"
    )

    with st.form(form_key):

        reviewer = st.text_input(
            "Reviewer Name",
            value=(
                existing_review["reviewer"]
                if existing_review
                else ""
            )
        )

        decision = st.radio(
            "Certification Decision",
            ["APPROVED", "REJECTED"],
            index=(
                1 if existing_review
                and existing_review["decision"] == "REJECTED"
                else 0
            ),
            horizontal=True
        )

        comments = st.text_area(
            "Reviewer Comments",
            value=(
                existing_review["comments"] or ""
                if existing_review
                else ""
            ),
            placeholder=(
                "Explain why the generated SQL "
                "is correct or incorrect."
            )
        )

        submitted = st.form_submit_button(
            "Save Certification",
            type="primary"
        )

    if submitted:

        if not reviewer.strip():
            st.error("Enter a reviewer name.")

        elif decision == "REJECTED" and not comments.strip():
            st.error(
                "Provide a reason for rejecting this query."
            )

        elif (
            decision == "APPROVED"
            and evaluation_status != "PASS"
            and not comments.strip()
        ):
            st.error(
                "Explain why you are overriding "
                "a failed automated evaluation."
            )

        else:
            save_review(
                selected_version,
                review_question_id,
                generated_sql,
                decision,
                reviewer,
                comments
            )

            st.success("Certification saved!")
            st.rerun()

# ---------------------------
# Certification Summary
# ---------------------------

st.header("Certification Summary")

review_statuses = []

for _, item in results.iterrows():
    review = get_review(
        selected_version,
        item["question_id"],
        str(item.get("generated_sql", ""))
    )

    status = review["decision"] if review else "PENDING"
    review_statuses.append(status)

approved_count = review_statuses.count("APPROVED")
rejected_count = review_statuses.count("REJECTED")
pending_count = review_statuses.count("PENDING")

total_count = len(review_statuses)

if total_count > 0:
    approved_pct = approved_count / total_count * 100
    rejected_pct = rejected_count / total_count * 100
    pending_pct = pending_count / total_count * 100
else:
    approved_pct = rejected_pct = pending_pct = 0


# Summary metric cards
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Approved",
        value=approved_count
    )

with col2:
    st.metric(
        label="Rejected",
        value=rejected_count
    )

with col3:
    st.metric(
        label="Pending Review",
        value=pending_count
    )


# Horizontal stacked status bar
st.markdown("### Certification Progress")

if total_count > 0:
    st.markdown(
        f"""
        <div style="
            display: flex;
            width: 100%;
            height: 22px;
            border-radius: 8px;
            overflow: hidden;
            background-color: #e5e7eb;
        ">
            <div style="
                width: {approved_pct:.4f}%;
                background-color: #16a34a;
            "></div>

            <div style="
                width: {rejected_pct:.4f}%;
                background-color: #dc2626;
            "></div>

            <div style="
                width: {pending_pct:.4f}%;
                background-color: #94a3b8;
            "></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        f"Approved: {approved_pct:.1f}%  |  "
        f"Rejected: {rejected_pct:.1f}%  |  "
        f"Pending: {pending_pct:.1f}%"
    )

else:
    st.info("No questions available for certification.")