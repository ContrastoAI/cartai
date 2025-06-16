"""
Utility functions and constants for LLM agents.
"""

from enum import StrEnum
from typing import List


class LowCostOpenAIModels(StrEnum):
    """
    Enumeration of low-cost OpenAI models.

    These models provide a good balance between performance and cost,
    making them suitable for various applications where budget is a concern.
    """

    GPT_4_1_NANO = "gpt-4.1-nano"
    GPT_4_1_MINI = "gpt-4.1-mini"
    O4_MINI = "o4-mini"
    O3_MINI = "o3-mini"
    O1_MINI = "o1-mini"
    GPT_4O_MINI = "gpt-4o-mini"

    @classmethod
    def list(cls) -> List[str]:
        """
        Returns a list of all low-cost OpenAI model names as strings.

        Returns:
            List[str]: A list of model names.
        """
        return [model.value for model in cls]
