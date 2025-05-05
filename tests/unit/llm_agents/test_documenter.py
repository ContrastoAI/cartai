import pytest
from pathlib import Path
from cartai.llm_agents.documenter import AIDocumenter


@pytest.fixture
def documenter():
    """Create a basic documenter instance for testing"""
    return AIDocumenter(
        model="test-model",
        template_dir=Path("/tmp/templates"),  # Use a test directory
    )


def test_load_template_not_found(documenter):
    """Test handling of missing template file"""
    with pytest.raises(FileNotFoundError):
        documenter._load_template("nonexistent.txt")
