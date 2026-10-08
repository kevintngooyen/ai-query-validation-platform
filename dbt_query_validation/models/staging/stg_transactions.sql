select
    transaction_id,
    order_id,
    transaction_type,
    transaction_amount
from {{ source('raw', 'TRANSACTIONS') }}
