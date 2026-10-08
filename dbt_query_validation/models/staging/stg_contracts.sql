select
    contract_id,
    customer_id,
    discount_rate,
    cast(start_date as date) as start_date,
    cast(end_date as date) as end_date
from {{ source('raw', 'CONTRACTS') }}
