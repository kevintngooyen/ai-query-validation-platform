select
    product_id,
    product_name,
    category,
    price
from {{ source('raw', 'PRODUCTS') }}
