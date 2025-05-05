"""
AIDocumenter class for generating documentation using LLM models.
"""

import os
from pathlib import Path
from typing import Dict, Any
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

    model: str | None = Field(
        default="gpt-4o-mini", description="The LLM model to use for generation"
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

        # Extract and return the generated content
        return response.choices[0].message.content

    def save_documentation(self, content: str, output_path: Path) -> None:
        """
        Save generated documentation to a file.

        Args:
            content: The documentation content to save
            output_path: Path where the documentation should be saved
        """
        output_path = Path(output_path)
        output_path.write_text(content)
        print(f"Documentation saved to {output_path}")
