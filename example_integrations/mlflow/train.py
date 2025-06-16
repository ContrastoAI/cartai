import mlflow
import numpy as np
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.ensemble import RandomForestClassifier  # type: ignore
from sklearn.metrics import accuracy_score, precision_score, recall_score  # type: ignore
import logging
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get MLflow tracking URI from environment
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
logger.info(f"Using MLflow tracking URI: {MLFLOW_TRACKING_URI}")


def generate_sample_data(n_samples=1000):
    """Generate synthetic data for binary classification"""
    np.random.seed(42)
    X = np.random.randn(n_samples, 4)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y


def train_model():
    """Train a random forest classifier and log metrics with MLflow"""
    logger.info("Starting model training")

    # Generate data
    X, y = generate_sample_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Set experiment
    experiment_name = "random_forest_demo"
    try:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            mlflow.create_experiment(experiment_name)
    except Exception as e:
        logger.error(f"Error setting up experiment: {str(e)}")
        raise

    mlflow.set_experiment(experiment_name)

    # Model parameters
    params = {"n_estimators": 100, "max_depth": 5, "random_state": 42}

    with mlflow.start_run() as run:
        logger.info(f"MLflow Run ID: {run.info.run_id}")

        # Log parameters
        mlflow.log_params(params)

        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
        }

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log model
        mlflow.sklearn.log_model(model, "random_forest_model")

        logger.info(f"Training completed. Metrics: {metrics}")

        return run.info.run_id


if __name__ == "__main__":
    max_retries = 5
    retry_delay = 10

    for attempt in range(max_retries):
        try:
            run_id = train_model()
            logger.info(f"Training completed successfully. Run ID: {run_id}")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {retry_delay} seconds..."
                )
                time.sleep(retry_delay)
            else:
                logger.error(
                    f"All attempts failed. Last error: {str(e)}", exc_info=True
                )
                raise
