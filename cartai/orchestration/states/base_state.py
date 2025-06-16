"""Base state for orchestration workflows"""

import operator
from typing import Annotated, TypedDict, List


class BaseState(TypedDict):
    """Base state for all orchestration workflows"""

    messages: Annotated[List, operator.add]
    timestamp: str
    workflow_id: str
    environment: str
