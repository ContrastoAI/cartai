import json
import pytest
from unittest.mock import Mock, patch
from cartai.mcps.servers.mcp_mlflow import (
    _list_models,
    _list_experiments,
    _get_model_details,
    _get_system_info,
    MLflowTools,
)

# Mock data for testing
MOCK_MODEL = Mock()
MOCK_MODEL.name = "test_model"
MOCK_MODEL.creation_timestamp = 1609459200000
MOCK_MODEL.last_updated_timestamp = 1609545600000
MOCK_MODEL.description = "Test model description"
MOCK_MODEL.tags = [Mock(key="tag1", value="value1")]
MOCK_MODEL.latest_versions = [
    Mock(
        version="1",
        status="READY",
        current_stage="Production",
        creation_timestamp=1609459200000,
        run_id="run1",
    )
]

MOCK_MODEL_VERSION = Mock()
MOCK_MODEL_VERSION.version = "1"
MOCK_MODEL_VERSION.status = "READY"
MOCK_MODEL_VERSION.current_stage = "Production"
MOCK_MODEL_VERSION.creation_timestamp = 1609459200000
MOCK_MODEL_VERSION.source = "s3://test-bucket/model"
MOCK_MODEL_VERSION.run_id = "run1"

MOCK_EXPERIMENT = Mock()
MOCK_EXPERIMENT.experiment_id = "exp1"
MOCK_EXPERIMENT.name = "test_experiment"
MOCK_EXPERIMENT.artifact_location = "s3://test-bucket"
MOCK_EXPERIMENT.lifecycle_stage = "active"
MOCK_EXPERIMENT.creation_time = 1609459200000
MOCK_EXPERIMENT.tags = [Mock(key="tag1", value="value1")]

# Create mock run info and data
mock_run_info = Mock()
mock_run_info.run_id = "run1"
mock_run_info.status = "FINISHED"
mock_run_info.start_time = 1609459200000
mock_run_info.end_time = 1609545600000
mock_run_info.artifact_uri = "s3://test-bucket/artifacts"

mock_run_data = Mock()
mock_run_data.metrics = {"accuracy": 0.95, "loss": 0.1}
mock_run_data.params = {"learning_rate": "0.001", "epochs": "10"}
mock_run_data.tags = [Mock(key="tag1", value="value1")]

MOCK_RUN = Mock()
MOCK_RUN.info = mock_run_info
MOCK_RUN.data = mock_run_data


@pytest.fixture
def mock_client():
    with patch("cartai.mcps.servers.mcp_mlflow.client") as mock:
        # Setup mock responses
        mock.search_registered_models.return_value = [MOCK_MODEL]
        mock.search_experiments.return_value = [MOCK_EXPERIMENT]
        mock.search_runs.return_value = [MOCK_RUN]
        mock.get_registered_model.return_value = MOCK_MODEL
        mock.get_run.return_value = MOCK_RUN
        mock.search_model_versions.return_value = [MOCK_MODEL_VERSION]
        yield mock


@pytest.fixture
def mock_mlflow():
    with patch("cartai.mcps.servers.mcp_mlflow.mlflow") as mock:
        mock.__version__ = "2.22.1"
        mock.get_tracking_uri.return_value = "http://localhost:5000"
        mock.get_registry_uri.return_value = "http://localhost:5000"
        yield mock


def test_format_timestamp():
    """Test the timestamp formatting utility."""
    # Test with valid timestamp
    timestamp = 1609459200000  # 2021-01-01 00:00:00 UTC
    assert MLflowTools._format_timestamp(timestamp) == "2021-01-01 00:00:00"

    # Test with None
    assert MLflowTools._format_timestamp(None) == "N/A"


def test_list_models(mock_client):
    """Test listing models functionality."""
    # Test basic listing
    result = _list_models()
    result_dict = json.loads(result)

    assert result_dict["total_models"] == 1
    assert result_dict["models"][0]["name"] == "test_model"
    assert result_dict["models"][0]["description"] == "Test model description"
    assert result_dict["models"][0]["tags"] == {"tag1": "value1"}

    # Test filtering
    result = _list_models(name_contains="test")
    result_dict = json.loads(result)
    assert result_dict["total_models"] == 1


def test_list_experiments(mock_client):
    """Test listing experiments functionality."""
    # Test basic listing
    result = _list_experiments()
    result_dict = json.loads(result)

    assert result_dict["total_experiments"] == 1
    assert result_dict["experiments"][0]["name"] == "test_experiment"
    assert result_dict["experiments"][0]["experiment_id"] == "exp1"

    # Test filtering
    result = _list_experiments(name_contains="test")
    result_dict = json.loads(result)
    assert result_dict["total_experiments"] == 1

    # Test error handling
    mock_client.search_experiments.side_effect = Exception("Test error")
    result = _list_experiments()
    result_dict = json.loads(result)
    assert "error" in result_dict


def test_get_model_details(mock_client):
    """Test getting model details functionality."""
    # Test getting model details
    result = _get_model_details("test_model")
    result_dict = json.loads(result)

    assert result_dict["name"] == "test_model"
    assert result_dict["description"] == "Test model description"
    assert len(result_dict["versions"]) == 1
    assert result_dict["versions"][0]["version"] == "1"

    # Test error handling
    mock_client.get_registered_model.side_effect = Exception("Test error")
    result = _get_model_details("test_model")
    result_dict = json.loads(result)
    assert "error" in result_dict


def test_get_system_info(mock_client, mock_mlflow):
    """Test getting system information functionality."""
    # Test getting system info
    result = _get_system_info()
    result_dict = json.loads(result)

    assert "mlflow_version" in result_dict
    assert "tracking_uri" in result_dict
    assert "experiment_count" in result_dict
    assert "model_count" in result_dict
    assert "active_runs" in result_dict
