#!/bin/bash

# Start MLflow server in background
mlflow server --host 0.0.0.0 --port 5000 &
MLFLOW_PID=$!

# Wait for MLflow server to start
sleep 5

# Run the training script
python train.py

# Keep MLflow server running
wait $MLFLOW_PID
