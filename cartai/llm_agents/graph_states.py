import operator
from typing import Annotated, TypedDict, Any


class CartaiState(TypedDict):
    messages: Annotated[list, operator.add]


class CartaiDynamicState(TypedDict):
    messages: Annotated[list, operator.add]
    project_context: Annotated[dict[str, Any], operator.or_]
    outputs: Annotated[list[tuple[str, Any]], operator.add]
