import pytest
import os
from pathlib import Path
from jinja2 import Template

from cartai.llm_agents.documenter import AIDocumenter
from cartai.llm_agents.utils import LowCostOpenAIModels


@pytest.fixture
def documenter():
    """Create a basic documenter instance for testing"""
    return AIDocumenter(
        model=LowCostOpenAIModels.GPT_4O_MINI,
        template_dir=Path("cartai/llm_agents/templates"),  # Use a test directory
    )


def test_load_template_not_found(documenter):
    """Test handling of missing template file"""
    with pytest.raises(FileNotFoundError):
        documenter._load_template("nonexistent.txt")


def test_load_readme_template(documenter):
    """Test loading a template file"""
    template = documenter._load_template("readme.jinja")
    assert template is not None
    assert isinstance(template, Template)
    assert template.render() is not None


def test_generate_readme_no_api_key(documenter):
    """Test generating a README with no API key"""
    os.environ["OPENAI_API_KEY"] = ""
    with pytest.raises(ValueError):
        documenter.generate("readme.jinja", {})
