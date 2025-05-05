"""
AIDocumenter class for generating documentation using LLM models.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from cartai.llm_agents.utils import LowCostOpenAIModels
from cartai.core import ProjectParser
from litellm import completion
from jinja2 import Template
from pydantic import BaseModel, Field, SecretStr
import dotenv

dotenv.load_dotenv()


class AIDocumenter(BaseModel):
    """
    A class that uses LLMs to generate documentation based on templates.

    This class leverages the litellm library to interact with various LLM providers
    and generate documentation based on provided templates and context.
    """

    model: LowCostOpenAIModels | None = Field(
        default=LowCostOpenAIModels.GPT_4O_MINI,
        description="The LLM model to use for generation",
    )
    api_key: SecretStr | None = Field(
        default=None, description="The API key to use for the LLM provider"
    )
    template_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent / "templates",
        description="Directory containing templates",
    )

    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context: Any) -> None:
        """Ensure template directory exists after initialization"""
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def _load_template(self, template_name: str) -> Template:
        """
        Load a template from the template directory.

        Args:
            template_name: Name of the template file

        Returns:
            The template content as a string

        Raises:
            FileNotFoundError: If the template doesn't exist
        """
        template_path = self.template_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, "r") as f:
            return Template(f.read())

    def _parse_code_structure(self, code_path: Optional[Union[str, Path]]) -> str:
        """
        Parse the code structure if a path is provided.

        Args:
            code_path: Path to the code directory

        Returns:
            A string representation of the code structure or empty string if no path
        """
        if not code_path:
            return ""

        parser = ProjectParser(include_content=False, summarize_large_files=True)

        try:
            return parser.get_summary(code_path)
        except Exception as e:
            # Log the error but continue with an empty structure
            print(f"Error parsing code structure: {e}")
            return ""

    def generate(
        self,
        template_name: str,
        context: Dict[Any, Any],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate documentation using a template and context.

        Args:
            template_name: Name of the template file to use
            context: Dictionary of variables to inject into the template
            temperature: Controls randomness (0-1)
            max_tokens: Maximum tokens in the response

        Returns:
            Generated documentation as a string

        Raises:
            ValueError: If no API key is provided either through initialization or environment variable
        """
        # Process code structure if provided
        # if "structure" in context and context["structure"]:
        #    context["structure"] = self._parse_code_structure(context["structure"])

        # Load the template
        template_content = self._load_template(template_name)

        # Format the template with the context
        prompt = template_content.render(context)

        # Check for API key availability
        api_key = (
            self.api_key.get_secret_value()
            if self.api_key
            else os.getenv("OPENAI_API_KEY")
        )
        if not api_key:
            raise ValueError(
                "No API key provided. Please either pass api_key when initializing AIDocumenter "
                "or set the OPENAI_API_KEY environment variable."
            )

        # Generate the documentation using litellm
        response = completion(
            model=self.model,
            api_key=api_key,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    # probably outside the class scope
    # def save_documentation(self, content: str, output_path: Path) -> None:
    #    """
    #    Save generated documentation to a file.


#
#    Args:
#        content: The documentation content to save
#        output_path: Path where the documentation should be saved
#    """
#    output_path = Path(output_path)
#    output_path.write_text(content, encoding='utf-8')
#    print(f"Documentation saved to {output_path}")
