import pytest
from pathlib import Path
from cartai.llm_agents.documenter import AIDocumenter
from cartai.llm_agents.utils import LowCostOpenAIModels


@pytest.fixture
def documenter():
    """Create a basic documenter instance for testing"""
    return AIDocumenter(
        model=LowCostOpenAIModels.GPT_4O_MINI,
        template_dir=Path("/tmp/templates"),  # Use a test directory
    )


def test_load_template_not_found(documenter):
    """Test handling of missing template file"""
    with pytest.raises(FileNotFoundError):
        documenter._load_template("nonexistent.txt")
