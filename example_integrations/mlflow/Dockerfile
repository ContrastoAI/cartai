FROM python:3.9-slim

WORKDIR /mlflow

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install requirements (with verbose output)
COPY requirements.txt .
RUN pip install --no-cache-dir -v -r requirements.txt

# Copy the application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Set MLflow environment
ENV MLFLOW_TRACKING_URI=http://localhost:5000
ENV GIT_PYTHON_REFRESH=quiet

# Expose MLflow UI port
EXPOSE 5000

# Run both MLflow server and training script
CMD ["./start.sh"]
