from pathlib import Path
import random

import pandas as pd
from faker import Faker


# -----------------------------
# Setup
# -----------------------------

fake = Faker()

random.seed(42)
Faker.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "generated"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Configuration
# -----------------------------

NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 25
NUM_ORDERS = 10000
NUM_CONTRACTS = 500


# -----------------------------
# Customers
# -----------------------------

customers = []

regions = [
    "West",
    "East",
    "Central",
    "South"
]

segments = [
    "Enterprise",
    "Mid-Market",
    "SMB"
]

for customer_id in range(1, NUM_CUSTOMERS + 1):

    customers.append({
        "customer_id": customer_id,
        "customer_name": fake.company(),
        "region": random.choice(regions),
        "segment": random.choice(segments)
    })


customers_df = pd.DataFrame(customers)

customers_df.to_csv(
    OUTPUT_DIR / "customers.csv",
    index=False
)


# -----------------------------
# Products
# -----------------------------

products = []

categories = [
    "Analytics",
    "Data",
    "Security",
    "Software"
]

for product_id in range(1, NUM_PRODUCTS + 1):

    products.append({
        "product_id": product_id,
        "product_name": f"Product {product_id}",
        "category": random.choice(categories),
        "price": round(random.uniform(50, 1000), 2)
    })


products_df = pd.DataFrame(products)

products_df.to_csv(
    OUTPUT_DIR / "products.csv",
    index=False
)


# -----------------------------
# Contracts
# -----------------------------

contracts = []

for contract_id in range(1, NUM_CONTRACTS + 1):

    start_date = fake.date_between(
        start_date="-3y",
        end_date="-6m"
    )

    end_date = fake.date_between(
        start_date="today",
        end_date="+2y"
    )

    contracts.append({
        "contract_id": contract_id,
        "customer_id": random.randint(
            1,
            NUM_CUSTOMERS
        ),
        "discount_rate": round(
            random.uniform(0.05, 0.25),
            2
        ),
        "start_date": start_date,
        "end_date": end_date
    })


contracts_df = pd.DataFrame(contracts)

contracts_df.to_csv(
    OUTPUT_DIR / "contracts.csv",
    index=False
)


# -----------------------------
# Orders
# -----------------------------

orders = []

for order_id in range(1, NUM_ORDERS + 1):

    customer_id = random.randint(
        1,
        NUM_CUSTOMERS
    )

    product_id = random.randint(
        1,
        NUM_PRODUCTS
    )

    quantity = random.randint(1, 10)

    product_price = products_df.loc[
        products_df["product_id"] == product_id,
        "price"
    ].iloc[0]

    gross_amount = quantity * product_price

    order_date = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "product_id": product_id,
        "order_date": order_date,
        "quantity": quantity,
        "gross_amount": round(
            gross_amount,
            2
        )
    })


orders_df = pd.DataFrame(orders)

orders_df.to_csv(
    OUTPUT_DIR / "orders.csv",
    index=False
)


# -----------------------------
# Payments
# -----------------------------

payments = []

for payment_id, order in orders_df.iterrows():

    payment_status = random.choice([
        "Paid",
        "Paid",
        "Paid",
        "Paid",
        "Pending",
        "Failed"
    ])

    if payment_status == "Paid":
        payment_amount = order["gross_amount"]
    else:
        payment_amount = 0

    payment_date = fake.date_between(
        start_date=order["order_date"],
        end_date="today"
    )

    payments.append({
        "payment_id": payment_id + 1,
        "order_id": order["order_id"],
        "payment_date": payment_date,
        "payment_amount": round(
            payment_amount,
            2
        ),
        "payment_status": payment_status
    })


payments_df = pd.DataFrame(payments)

payments_df.to_csv(
    OUTPUT_DIR / "payments.csv",
    index=False
)


# -----------------------------
# Transactions
# -----------------------------

transactions = []

for transaction_id, order in orders_df.iterrows():

    transaction_type = random.choices(
        ["Sale", "Refund", "Adjustment"],
        weights=[85, 10, 5],
        k=1
    )[0]

    if transaction_type == "Sale":
        transaction_amount = order["gross_amount"]

    elif transaction_type == "Refund":
        transaction_amount = -round(
            random.uniform(
                1,
                order["gross_amount"]
            ),
            2
        )

    else:
        transaction_amount = round(
            random.uniform(
                -100,
                100
            ),
            2
        )

    transactions.append({
        "transaction_id": transaction_id + 1,
        "order_id": order["order_id"],
        "transaction_type": transaction_type,
        "transaction_amount": transaction_amount
    })


transactions_df = pd.DataFrame(transactions)

transactions_df.to_csv(
    OUTPUT_DIR / "transactions.csv",
    index=False
)


# -----------------------------
# Summary
# -----------------------------

print()
print("Synthetic data generated successfully.")
print()

print(
    f"Customers:    {len(customers_df):,}"
)

print(
    f"Products:     {len(products_df):,}"
)

print(
    f"Contracts:    {len(contracts_df):,}"
)

print(
    f"Orders:       {len(orders_df):,}"
)

print(
    f"Payments:     {len(payments_df):,}"
)

print(
    f"Transactions: {len(transactions_df):,}"
)

print()

print(
    f"Files saved to: {OUTPUT_DIR}"
)
