select
    customer_id,
    customer_name,
    region,
    segment
from {{ source('raw', 'CUSTOMERS') }}
