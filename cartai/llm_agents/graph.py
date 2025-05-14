import asyncio
from pathlib import Path
from typing import Any
from pydantic import BaseModel, ConfigDict
from cartai.llm_agents.graph_states import CartaiDynamicState
from langgraph.graph import StateGraph, START, END

from cartai.llm_agents.utils.yaml_utils import YAMLUtils


class CartaiGraph(BaseModel):
    """
    A class that uses LLMs to generate a graph of the project.
    """

    config_file: Path

    _workflow: StateGraph = None  # type: ignore

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: Any) -> None:
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        with open(self.config_file, "r") as file:
            config = YAMLUtils.safe_load(file)

        self._workflow: StateGraph = StateGraph(CartaiDynamicState)

        for agent in config["agents"]:
            # Get the agent logic - either from a string path or YAML constructor
            logic = agent["logic"]
            if isinstance(logic, str):
                logic = YAMLUtils.import_class(logic)

            # Initialize the agent if needed and add to workflow
            if agent.get("params"):
                self._workflow.add_node(agent["name"], logic(**agent["params"]).run)
            else:
                self._workflow.add_node(agent["name"], logic)

            # Add edges
            if agent.get("parent"):
                self._workflow.add_edge(agent["parent"], agent["name"])
            else:
                self._workflow.add_edge(START, agent["name"])

        self._workflow.add_edge(agent["name"], END)

    def compile(self):
        graph = self._workflow.compile()
        return graph

    def get_graph(self, ascii=False, **kwargs):
        if ascii:
            return self._workflow.compile().get_graph(**kwargs).print_ascii()
        else:
            return self._workflow.compile().get_graph(**kwargs)

    def invoke(self, state: CartaiDynamicState):
        return self._workflow.compile().invoke(state)

    async def ainvoke(self, state: CartaiDynamicState):
        return await self._workflow.compile().ainvoke(state)


if __name__ == "__main__":
    graph = CartaiGraph(config_file=Path("langgraph_config/dummy_config.yaml"))
    asyncio.run(
        graph.ainvoke(
            CartaiDynamicState(
                messages=["Hello, world!"],
                project_context={},
                outputs=[],
            )
        )
    )
