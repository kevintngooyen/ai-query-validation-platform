with base as (

    select *
    from {{ ref('int_orders_payments') }}

)

select
    customer_id,
    customer_name,
    region,
    segment,

    product_id,
    product_name,
    category,

    count(distinct order_id) as order_count,

    sum(gross_amount) as gross_revenue,

    sum(coalesce(payment_amount, 0)) as total_payments,

    sum(outstanding_amount) as outstanding_amount,

    avg(gross_amount) as average_order_value,

    case
        when sum(gross_amount) = 0 then 0
        else sum(coalesce(payment_amount, 0)) / sum(gross_amount)
    end as payment_rate

from base

group by
    customer_id,
    customer_name,
    region,
    segment,
    product_id,
    product_name,
    category
