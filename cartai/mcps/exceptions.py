"""
MCP-specific exceptions
"""


class MCPError(Exception):
    """Base exception for MCP-related errors"""

    pass


class MCPNotFoundError(MCPError):
    """Raised when a requested MCP is not found or registered"""

    pass


class MCPInitializationError(MCPError):
    """Raised when MCP initialization fails"""

    pass


class MCPConnectionError(MCPError):
    """Raised when MCP connection fails"""

    pass


class MCPHealthCheckError(MCPError):
    """Raised when MCP health check fails"""

    pass
