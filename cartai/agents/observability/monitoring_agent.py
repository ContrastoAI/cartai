import logging
import json
from typing import Dict, Any, List
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from cartai.agents.base.mcp_aware_agent import MCPAwareAgent
from cartai.agents.prompts import MCP_TOOLS_GUIDANCE

logger = logging.getLogger(__name__)


class MonitoringAgent(MCPAwareAgent):
    """
    Observability agent that monitors ML experiments and system health.
    Monitors ML experiments, collects metrics, and detects anomalies.

    Responsibilities:
    - Collect experiment metrics from MLflow
    - Monitor system performance
    - Detect anomalies and trends
    - Generate alerts and reports
    """

    def __init__(
        self,
        mcp_client=None,
        monitoring_config: Dict[str, Any] | None = None,
        core_prompt: str | None = None,
        instructions: str | None = None,
        **kwargs,
    ):
        """
        Initialize MonitoringAgent.

        Args:
            mcp_client: Optional MCP client instance
            monitoring_config: Monitoring configuration (thresholds, intervals, etc.)
        """
        super().__init__(mcp_client=mcp_client, **kwargs)

        self.monitoring_config = monitoring_config or self._get_default_config()
        self.metrics_history: List[Dict] = []
        self.alerts: List[Dict] = []
        self.core_prompt = core_prompt
        self.instructions = instructions

    def _get_default_config(self) -> Dict[str, Any]:
        """Default monitoring configuration"""
        return {
            "thresholds": {
                "accuracy_degradation_threshold": 0.05,
                "latency_threshold_ms": 1000,
                "error_rate_threshold": 0.05,
                "memory_usage_threshold": 0.85,
            },
            "monitoring_intervals": {
                "metrics_collection_minutes": 5,
                "health_check_minutes": 1,
                "alert_cooldown_minutes": 30,
            },
            "alert_settings": {
                "enable_drift_alerts": True,
                "enable_performance_alerts": True,
                "enable_system_alerts": True,
            },
        }

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute monitoring and analysis using LLM reasoning.

        Args:
            state: Current pipeline state

        Returns:
            Updated state with monitoring results
        """
        logger.info("MonitoringAgent: Starting LLM-powered monitoring analysis")

        tools = await self.get_tools()

        # Create agent with debugging enabled and proper configuration
        agent = create_react_agent(
            model="openai:gpt-4o-mini",
            tools=tools,  # type: ignore[arg-type]
            debug=True,
            version="v2",
            name="monitoring_agent",
        )

        context = None  # self._prepare_monitoring_context(state)

        system_prompt = f"{self.core_prompt}\n\n{MCP_TOOLS_GUIDANCE}"
        user_prompt = f"""
        {self.instructions}

        Context:
        {context}

        Tasks:
        1. Generate monitoring insights and recommendations
        2. Provide a system health status (HEALTHY/DEGRADED/UNHEALTHY)

        If there is an error in tool usage, please incorporate the feedback from the error message, think how to solve it perfectly and try to fix it and try again.

        Please respond with a JSON structure containing:
        {{
            "system_health": "HEALTHY|DEGRADED|UNHEALTHY",
            "model_metrics": {{"accuracy": 0.0, "precision": 0.0, ...}},
            "alerts": [list of alert objects],
            "analysis_summary": "text summary",
            "recommendations": [list of recommendations],
            "actions_taken": [list of actions taken]
        }}
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        # Get LLM analysis with debugging
        logger.info("Starting agent execution with debugging enabled")
        response = await agent.ainvoke({"messages": messages})
        logger.info("Agent execution completed")

        # Extract and parse LLM response
        formatted_response = self._format_response(response)
        print(formatted_response)
        analysis_results = self._extract_analysis_results(response)

        # Update state with LLM analysis
        state.update(
            {
                "model_metrics": analysis_results.get("model_metrics", {}),
                "monitoring_analysis": analysis_results,
                "alerts_generated": analysis_results.get("alerts", []),
                "monitoring_timestamp": datetime.utcnow().isoformat(),
                "system_health": analysis_results.get("system_health", "UNKNOWN"),
                "actions_taken": analysis_results.get("actions_taken", []),
            }
        )

        logger.info(
            f"MonitoringAgent: LLM analysis completed - Health: {analysis_results.get('system_health')}"
        )
        return state

    def _prepare_monitoring_context(self, state: Dict[str, Any]) -> str:
        """Prepare context information for LLM analysis"""
        context_parts = []

        # Experiment information
        if "experiment_id" in state:
            context_parts.append(f"Experiment ID: {state['experiment_id']}")
        if "model_name" in state:
            context_parts.append(f"Model Name: {state['model_name']}")
        if "run_id" in state:
            context_parts.append(f"Run ID: {state['run_id']}")

        if "model_metrics" in state:
            context_parts.append(
                f"Previous Metrics: {json.dumps(state['model_metrics'], indent=2)}"
            )

        if hasattr(self, "monitoring_config"):
            context_parts.append(
                f"Monitoring Configuration: {json.dumps(self.monitoring_config, indent=2)}"
            )

        if "workflow_stage" in state:
            context_parts.append(f"Workflow Stage: {state['workflow_stage']}")

        if "error_messages" in state and state["error_messages"]:
            context_parts.append(f"Previous Errors: {state['error_messages']}")

        return (
            "\n".join(context_parts)
            if context_parts
            else "No context information available"
        )
    
    def _format_response(self, response: Dict[str, Any]) -> str:
        """
        Format the LLM response messages into a beautiful, human-readable format.
        
        Args:
            response: The raw response dictionary from the LLM
            
        Returns:
            A formatted string containing the conversation flow
        """
        if not response or not response.get("messages"):
            return "No messages found in response"
            
        formatted_parts = []
        formatted_parts.append("🤖 Monitoring Agent Analysis")
        formatted_parts.append("=" * 50)
        
        for idx, msg in enumerate(response.get("messages", []), 1):
            # Add message separator
            formatted_parts.append(f"\n📝 Step {idx}")
            formatted_parts.append("-" * 50)
            
            # Format based on message type
            if hasattr(msg, "tool_calls") and not idx == len(response.get("messages", [])):
                # Tool execution message
                formatted_parts.append("🔧 Tool Execution:")
                for tool_call in msg.tool_calls:
                    tool_name = getattr(tool_call, "name", "Unknown Tool")
                    formatted_parts.append(f"  Tool: {tool_name}")
                    if hasattr(tool_call, "arguments"):
                        args = json.dumps(tool_call.arguments, indent=2)
                        formatted_parts.append("  Arguments:")
                        formatted_parts.extend(f"    {line}" for line in args.splitlines())
                        
            elif hasattr(msg, "tool_responses"):
                # Tool response message
                formatted_parts.append("📊 Tool Response:")
                for resp in msg.tool_responses:
                    formatted_parts.append(f"  {resp[:200]}...")
                    
            elif hasattr(msg, "content") and msg.content:
                # Regular message content
                if "```json" in msg.content:
                    # Handle JSON blocks specially
                    parts = msg.content.split("```")
                    for part in parts:
                        if part.startswith("json"):
                            try:
                                json_obj = json.loads(part[4:].strip())
                                formatted_parts.append(json.dumps(json_obj, indent=2))
                            except:
                                formatted_parts.append(part)
                        elif part.strip():
                            formatted_parts.append(part.strip())
                else:
                    formatted_parts.append(msg.content.strip())
            
            else:
                # Unknown message type
                formatted_parts.append("📄 Message:")
                formatted_parts.append(str(msg))
        
        # Add final separator
        formatted_parts.append("=" * 50)
        
        return "\n".join(formatted_parts)

    def _extract_last_message(self, llm_response) -> str:
        """Extract the last message from the LLM response"""
        for msg in reversed(llm_response.get("messages", [])):
            if hasattr(msg, "content") and msg.content:
                return msg.content
        return ""

    def _extract_analysis_results(self, llm_response) -> Dict[str, Any]:
        """Extract and parse analysis results from LLM response"""
        try:
            # Get the final message from the response
            final_message = None
            for msg in reversed(llm_response.get("messages", [])):
                if (
                    hasattr(msg, "content")
                    and msg.content
                    and not hasattr(msg, "tool_calls")
                ):
                    final_message = msg
                    break

            if not final_message:
                logger.warning("No final message found in LLM response")
                return {}

            content = final_message.content

            # Try to extract JSON from the response
            try:
                # Look for JSON block in the response
                import re

                json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(1))
                else:
                    # Try to parse the entire content as JSON
                    analysis = json.loads(content)

                # Validate required fields
                required_fields = ["system_health", "model_metrics"]
                for field in required_fields:
                    if field not in analysis:
                        logger.warning(
                            f"Missing required field '{field}' in LLM response"
                        )
                        analysis[field] = {} if field == "model_metrics" else "UNKNOWN"

                return analysis

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM response: {e}")
                logger.debug(f"LLM response content: {content}")
                return {}

        except Exception as e:
            logger.error(f"Error extracting analysis results: {e}")
            return {}
