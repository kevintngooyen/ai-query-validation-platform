import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from semantic_context import BUSINESS_METRICS, TABLE_CONTEXT


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def build_prompt(question):
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
- Generate valid Snowflake SQL.
- Use only MART_BUSINESS_METRICS.
- Use the fully qualified table name:
  AI_QUERY_VALIDATION.DBT_DEV.MART_BUSINESS_METRICS
- Do not invent columns.
- Follow the provided business metric definitions.
- Return only SQL.
- Do not include markdown.
- Do not include explanations.

Business question:

{question}
"""

    return prompt


def generate_sql(question):
    prompt = build_prompt(question)

    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt
    )

    sql = response.output_text.strip()

    return sql


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Please provide a business question.")
        print()
        print(
            'Example: python ai/generate_sql.py '
            '"Which customer generated the most gross revenue?"'
        )
        sys.exit(1)

    question = sys.argv[1]

    sql = generate_sql(question)

    print()
    print("Business Question:")
    print(question)

    print()
    print("Generated SQL:")
    print(sql)
