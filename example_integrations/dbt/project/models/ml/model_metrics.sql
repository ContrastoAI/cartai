{{ config(materialized='table') }}

WITH mock_metrics AS (
    SELECT
        'churn_prediction_v1' as model_name,
        'RandomForestClassifier' as model_type,
        0.85 as accuracy,
        0.78 as precision,
        0.82 as recall,
        0.80 as f1_score,
        '2024-03-14 10:00:00'::timestamp as training_completed_at,
        '{"max_depth": 10, "n_estimators": 100, "random_state": 42}'::jsonb as hyperparameters,
        '{{ ref("training_data") }}' as training_data_source,
        '{{ ref("customer_features") }}' as feature_source,
        '{{ ref("raw_customer_data") }}' as raw_data_source
    UNION ALL
    SELECT
        'churn_prediction_v2',
        'XGBoostClassifier',
        0.87,
        0.81,
        0.84,
        0.82,
        '2024-03-15 15:30:00'::timestamp,
        '{"max_depth": 8, "learning_rate": 0.1, "n_estimators": 200, "random_state": 42}'::jsonb,
        '{{ ref("training_data") }}',
        '{{ ref("customer_features") }}',
        '{{ ref("raw_customer_data") }}'
)

SELECT * FROM mock_metrics 