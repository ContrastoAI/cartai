from fastmcp import FastMCP
from cartai.oversight.mcp_servers.mcp_mlflow import mlflow_mcp

main_mcp = FastMCP(name="Contrasto CartAI MCP Server")
main_mcp.mount("mlflow", mlflow_mcp)


@main_mcp.tool
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    main_mcp.run(transport="streamable-http", host="127.0.0.1", port=9000)
