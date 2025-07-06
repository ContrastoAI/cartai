{{ config(materialized='table') }}

WITH customer_data AS (
    SELECT * FROM {{ ref('raw_customer_data') }}
),

feature_engineering AS (
    SELECT
        customer_id,
        customer_name,
        age,
        annual_income,
        account_status,
        created_at,
        -- Derived features
        CASE 
            WHEN age < 30 THEN 'Young'
            WHEN age < 50 THEN 'Middle'
            ELSE 'Senior'
        END as age_group,
        CASE 
            WHEN annual_income < 60000 THEN 'Low'
            WHEN annual_income < 80000 THEN 'Medium'
            ELSE 'High'
        END as income_bracket,
        EXTRACT(YEAR FROM created_at) as signup_year
    FROM customer_data
)

SELECT * FROM feature_engineering 