select
    order_id,
    customer_id,
    product_id,
    cast(order_date as date) as order_date,
    quantity,
    gross_amount
from {{ source('raw', 'ORDERS') }}
