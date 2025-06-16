import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic

from langchain_mcp_adapters.client import MultiServerMCPClient  # type: ignore

logger = logging.getLogger(__name__)

StateT = TypeVar("StateT", bound=Dict[str, Any])


class MCPAwareAgent(ABC, Generic[StateT]):
    """
    Base class for agents that use MCP tools.

    Provides:
    - MCP client access
    - Tool retrieval
    - Common agent patterns
    """

    def __init__(
        self, mcp_client: Optional[MultiServerMCPClient] = None, **kwargs: Any
    ) -> None:
        """
        Initialize MCP-aware agent.

        Args:
            mcp_client: Optional MCP client instance
            **kwargs: Additional agent-specific parameters
        """
        self.mcp_client = mcp_client
        self.name = self.__class__.__name__
        self._tools_cache: Optional[List[Dict[str, Any]]] = None

        # Store additional kwargs for agent-specific use
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def initialize(self) -> None:
        """Initialize the agent"""
        logger.info(f"Initializing {self.name}")

        if self.mcp_client:
            # Test connection by trying to get tools
            try:
                await self.get_tools()
                logger.info(f"{self.name} initialized with MCP client")
            except Exception as e:
                logger.warning(f"{self.name} MCP client test failed: {str(e)}")
                logger.info(f"{self.name} will run in mock mode")
        else:
            logger.info(f"{self.name} initialized without MCP client (mock mode)")

    async def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get MCP tools for this agent.

        Returns:
            List of available tools
        """
        if not self.mcp_client:
            logger.debug(f"{self.name}: No MCP client available, returning empty tools")
            return []

        try:
            if self._tools_cache is None:
                self._tools_cache = await self.mcp_client.get_tools()
                logger.debug(f"{self.name}: Retrieved {len(self._tools_cache)} tools")
            return self._tools_cache
        except Exception as e:
            logger.warning(f"{self.name}: Failed to get tools: {str(e)}")
            return []

    @abstractmethod
    async def run(self, state: StateT) -> StateT:
        """
        Execute the agent's main logic.

        Args:
            state: Current state/context for the agent

        Returns:
            Updated state after agent execution
        """
        pass

    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent"""
        return {
            "name": self.name,
            "type": "mcp_aware",
            "has_mcp_client": bool(self.mcp_client),
            "description": self.__doc__ or "No description available",
        }
