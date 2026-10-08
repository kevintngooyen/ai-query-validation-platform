select
    payment_id,
    order_id,
    cast(payment_date as date) as payment_date,
    payment_amount,
    payment_status
from {{ source('raw', 'PAYMENTS') }}
