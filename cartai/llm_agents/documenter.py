"""
AIDocumenter class for generating documentation using LLM models.
"""

import os
from pathlib import Path
from typing import Any
from cartai.llm_agents.graph_states import CartaiDynamicState
from cartai.llm_agents.utils.model_client_utils import LowCostOpenAIModels
from litellm import acompletion
from jinja2 import Template
from pydantic import BaseModel, Field, SecretStr, ConfigDict
import dotenv
import aiofiles

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

    template_name: str | None = Field(
        default=None, description="The name of the template to use"
    )
    context: dict[str, Any] = Field(
        default_factory=dict, description="The context to use for the template"
    )
    output: dict[str, Any] | None = Field(
        default=None, description="The output to use for the template"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: Any) -> None:
        """Ensure template directory exists after initialization"""
        self.template_dir.mkdir(parents=True, exist_ok=True)

    async def _load_template(self, template_name: str) -> Template:
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

        async with aiofiles.open(template_path, "r", encoding="utf-8") as f:
            content = await f.read()
            return Template(content)

    async def generate(
        self,
        template_name: str | None = None,
        context: dict[str, Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate documentation using a template and context.
        """
        if not template_name:
            if self.template_name:
                template_name = self.template_name
            else:
                raise ValueError("No template name provided.")

        if not context:
            context = self.context

        template_content = await self._load_template(template_name)

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
        response = await acompletion(
            model=self.model,
            api_key=api_key,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if self.output:
            with open(self.output["output_name"], "w", encoding="utf-8") as f:
                f.write(response.choices[0].message.content)

        return response.choices[0].message.content

    # adapter to LangGraph
    async def run(
        self,
        state: CartaiDynamicState,
    ) -> CartaiDynamicState:
        """
        Run the documenter.
        """
        if self.template_name is None:
            raise ValueError("template_name must be set")

        response = await self.generate(context=state["project_context"])

        return {
            "messages": [1],
            "outputs": [(f"Documenter_{self.template_name.split('.')[0]}", response)],
            "project_context": state.get("project_context", {}),
        }
