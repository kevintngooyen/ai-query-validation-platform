with orders as (

    select *
    from {{ ref('stg_orders') }}

),

customers as (

    select *
    from {{ ref('stg_customers') }}

),

products as (

    select *
    from {{ ref('stg_products') }}

),

payments as (

    select *
    from {{ ref('stg_payments') }}

)

select
    o.order_id,
    o.order_date,

    o.customer_id,
    c.customer_name,
    c.region,
    c.segment,

    o.product_id,
    p.product_name,
    p.category,

    o.quantity,
    o.gross_amount,

    pay.payment_id,
    pay.payment_date,
    pay.payment_amount,
    pay.payment_status,

    o.gross_amount - coalesce(pay.payment_amount, 0)
        as outstanding_amount

from orders o

left join customers c
    on o.customer_id = c.customer_id

left join products p
    on o.product_id = p.product_id

left join payments pay
    on o.order_id = pay.order_id
