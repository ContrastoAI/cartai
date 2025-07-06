{{ config(materialized='table') }}

WITH features AS (
    SELECT * FROM {{ ref('customer_features') }}
),

synthetic_targets AS (
    SELECT
        customer_id,
        -- Synthetic target variable (churn prediction)
        CASE
            WHEN account_status = 'Inactive' THEN 1
            WHEN income_bracket = 'Low' AND age_group = 'Young' THEN 1
            ELSE 0
        END as churned,
        -- Training/test split flag
        CASE
            WHEN MOD(customer_id, 3) = 0 THEN 'test'
            ELSE 'train'
        END as dataset_split
    FROM features
)

SELECT
    f.*,
    t.churned,
    t.dataset_split,
    CURRENT_TIMESTAMP as generated_at
FROM features f
JOIN synthetic_targets t ON f.customer_id = t.customer_id
