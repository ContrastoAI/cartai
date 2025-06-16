import os
import re
import logging
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List, cast
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from langchain_mcp_adapters.client import MultiServerMCPClient
from cartai.mcps.registry.mcp_registry import MCPRegistry
from cartai.orchestration.states.ml_pipeline_state import MLPipelineState
from cartai.llm_agents.utils.yaml_utils import YAMLUtils

logger = logging.getLogger(__name__)


class CartaiGraph(BaseModel):
    """
    Enhanced dynamic graph builder with MCP integration and conditional routing.

    Features:
    - Environment-aware configuration
    - MCP client integration
    - Conditional agent execution
    - Cross-domain state management
    """

    config_file: Path
    mcp_registry: Optional[MCPRegistry] = None
    environment: str = "development"

    _workflow: Optional[StateGraph] = None
    _config: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_post_init(self, __context: Any) -> None:
        """Initialize the enhanced graph"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        self._load_and_build_workflow()

    def _load_and_build_workflow(self):
        """Load configuration and build the workflow"""
        self._config = self._load_config()
        self._workflow = self._build_workflow()

    def _load_config(self) -> Dict:
        """Load configuration with environment variable substitution"""
        with open(self.config_file, "r") as file:
            config = YAMLUtils.safe_load(file)

        # Environment variable substitution
        config_str = YAMLUtils.safe_dump(config)
        config_str = re.sub(
            r"\$\{(\w+)\}", lambda m: os.getenv(m.group(1), ""), config_str
        )
        return YAMLUtils.safe_load(config_str)

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow from configuration"""
        logger.info(f"Building workflow for environment: {self.environment}")

        # Use MLPipelineState for cross-domain workflows
        workflow = StateGraph(MLPipelineState)

        # Add agents as nodes
        if self._config is not None:
            for agent_config in self._config.get("agents", []):
                self._add_agent_node(workflow, agent_config)

            # Add conditional routing if specified
            if "routing" in self._config:
                self._add_conditional_routing(workflow, self._config["routing"])
            else:
                # Add simple linear edges
                self._add_simple_edges(workflow)

        return workflow

    def _add_agent_node(self, workflow: StateGraph, agent_config: Dict):
        """Add an agent node to the workflow"""
        agent_name = agent_config["name"]

        # Get the agent class
        agent_logic = agent_config["logic"]
        if isinstance(agent_logic, str):
            agent_class = YAMLUtils.import_class(agent_logic)
        else:
            agent_class = agent_logic

        # Create agent instance with agent-specific MCP client
        agent_params = agent_config.get("params", {})
        agent_mcp_names = agent_config.get("mcps", [])

        if self.mcp_registry and agent_mcp_names:
            # Create filtered MCP client for this agent
            filtered_config = self.mcp_registry.get_filtered_client_config(
                agent_mcp_names
            )
            if filtered_config:
                agent_mcp_client = MultiServerMCPClient(filtered_config)
                agent_instance = agent_class(
                    mcp_client=agent_mcp_client, **agent_params
                )
                logger.info(
                    f"Agent '{agent_name}' created with MCPs: {agent_mcp_names}"
                )
            else:
                # No valid MCPs found for this agent
                agent_instance = agent_class(mcp_client=None, **agent_params)
                logger.warning(
                    f"Agent '{agent_name}' has no valid MCPs - running without MCP client"
                )
        else:
            # Create agent without MCP client
            agent_instance = agent_class(mcp_client=None, **agent_params)
            logger.info(f"Agent '{agent_name}' created without MCP client")

        # Wrap the agent run method with error handling and state management
        wrapped_agent = self._wrap_agent(agent_instance, agent_name)

        workflow.add_node(agent_name, wrapped_agent)
        logger.info(f"Added agent node: {agent_name}")

    def _wrap_agent(self, agent_instance, agent_name: str) -> Callable:
        """Wrap agent with error handling and state management"""

        async def wrapped_run(state: MLPipelineState) -> MLPipelineState:
            logger.info(f"Executing agent: {agent_name}")

            # Update state metadata
            state["current_agent"] = agent_name
            state["timestamp"] = datetime.utcnow().isoformat()

            try:
                # Initialize agent if needed
                await agent_instance.initialize()

                # Run the agent
                updated_state = await agent_instance.run(dict(state))

                # Merge the updated state
                state.update(updated_state)

                logger.info(f"Agent {agent_name} completed successfully")

            except Exception as e:
                breakpoint()
                error_msg = f"Agent {agent_name} failed: {str(e)}"
                logger.error(error_msg, exc_info=True)

                # Add error to state
                if "error_messages" not in state:
                    state["error_messages"] = []
                state["error_messages"].append(error_msg)

                # Decide whether to continue or halt
                if self._should_halt_on_error(agent_name, e):
                    raise

            return state

        return wrapped_run

    def _should_halt_on_error(self, agent_name: str, error: Exception) -> bool:
        """Determine if workflow should halt on this error"""
        # For now, continue on errors but log them
        # This could be made configurable per agent
        return False

    def _add_simple_edges(self, workflow: StateGraph):
        """Add simple linear edges between agents"""
        if self._config is None:
            return

        agents = self._config.get("agents", [])

        if not agents:
            return

        # Connect START to first agent
        workflow.add_edge(START, agents[0]["name"])

        # Connect agents linearly
        for i in range(len(agents) - 1):
            current_agent = agents[i]["name"]
            next_agent = agents[i + 1]["name"]
            workflow.add_edge(current_agent, next_agent)

        # Connect last agent to END
        workflow.add_edge(agents[-1]["name"], END)

    def _add_conditional_routing(
        self, workflow: StateGraph, routing_config: List[Dict]
    ):
        """Add conditional routing between agents"""
        # This is a simplified version - can be extended for complex routing
        for route in routing_config:
            from_agent = route["from"]
            conditions = route["conditions"]
            logic = route.get("logic", "")

            # Create routing function
            def create_router(route_logic: str, route_conditions: Dict):
                def router(state: MLPipelineState) -> str:
                    # Simple condition evaluation
                    # In a real implementation, this would be more sophisticated
                    try:
                        # Use eval with limited scope for safety
                        result = eval(route_logic, {"state": state})
                        return route_conditions.get(result, "default")
                    except Exception as e:
                        logger.warning(f"Routing logic failed: {e}")
                        return route_conditions.get("default", "end")

                return router

            workflow.add_conditional_edges(
                from_agent, create_router(logic, conditions), conditions
            )

    def compile(self) -> CompiledStateGraph:
        """Compile the workflow"""
        if not self._workflow:
            raise RuntimeError("Workflow not built. Call _build_workflow first.")

        return cast(CompiledStateGraph, self._workflow.compile())

    async def ainvoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow asynchronously"""
        # Log MCP registry status
        if self.mcp_registry:
            available_mcps = self.mcp_registry.get_available_mcps()
            logger.info(
                f"Executing workflow with MCP registry - Available MCPs: {available_mcps}"
            )
        else:
            logger.info("Executing workflow without MCP registry (mock mode)")

        # Create initial MLPipelineState
        ml_state = MLPipelineState(
            messages=[],
            timestamp=datetime.utcnow().isoformat(),
            workflow_id=f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            environment=self.environment,
            experiment_id=initial_state.get("experiment_id", "unknown"),
            model_name=initial_state.get("model_name", "unknown"),
            run_id=initial_state.get("run_id", "unknown"),
            data_quality_status="UNKNOWN",
            data_quality_score=0.0,
            model_metrics={},
            system_health="UNKNOWN",
            drift_detected=False,
            drift_alerts=[],
            drift_score=0.0,
            policy_violations=[],
            compliance_status="UNKNOWN",
            governance_decision="PENDING",
            cross_domain_decision="PENDING",
            decision_reason="",
            actions_taken=[],
            current_agent="",
            workflow_stage="STARTING",
            error_messages=[],
        )

        # Update with initial state values
        ml_state_dict = dict(ml_state)
        ml_state_dict.update(initial_state)
        ml_state = MLPipelineState(**ml_state_dict)

        # Execute workflow
        compiled_workflow = self.compile()
        result = await compiled_workflow.ainvoke(ml_state)

        return dict(result)

    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the configured workflow"""
        if not self._config:
            return {}

        return {
            "name": self._config.get("name", "Unknown"),
            "description": self._config.get("description", ""),
            "environment": self.environment,
            "agents": [agent["name"] for agent in self._config.get("agents", [])],
            "required_mcps": self._config.get("required_mcps", []),
            "config_file": str(self.config_file),
        }
