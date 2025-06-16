import argparse
import asyncio
from typing import Dict, Any
import logging
import textwrap
import os

from langchain_mcp_adapters.client import MultiServerMCPClient  # type: ignore
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

from dotenv import load_dotenv
from cartai.deprecated.oversight.settings import settings

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mlflow-mcp-client")

MLFLOW_SERVER_SCRIPT = settings.MLFLOW_SERVER_SCRIPT
MODEL_NAME = settings.MODEL_NAME


async def process_query(query: str) -> Dict[str, Any]:
    """
    Process a natural language query using LangChain agent with MCP tools.

    Args:
        query: The natural language query to process

    Returns:
        The agent's response
    """
    logger.info(f"Processing query: '{query}'")

    # System prompt for better MLflow interactions
    system_prompt = """
    You are a helpful assistant specialized in managing and querying MLflow tracking servers.
    You help users understand their machine learning experiments, models, and runs through
    natural language queries.

    When users ask questions about their MLflow tracking server, use the available tools to:
    1. Find relevant information from experiments, models, runs, and artifacts
    2. Compare metrics between different runs
    3. Provide clear and concise answers with insights and explanations
    4. Format numerical data appropriately (round to 4 decimal places when necessary)
    5. Show relevant metrics and parameters when discussing models and runs

    If a query is ambiguous, do your best to interpret it and provide a helpful response.
    Always provide context and explanations with your responses, not just raw data.

    If using the notionApi tool, take into account this:
    Problem	Fix
    children sent in patch-page	Remove children, only send properties
    Want to add text content	Use append-block-children API instead
    """
    try:
        # Set up server parameters
        headers = {
            "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
            "Notion-Version": "2022-06-28",
        }
        client = MultiServerMCPClient(
            {
                "mlflow": {
                    "url": MLFLOW_SERVER_SCRIPT,
                    "transport": "streamable_http",
                },
                "notionApi": {
                    "command": "docker",
                    "args": [
                        "run",
                        "--rm",
                        "-i",
                        "-e",
                        "OPENAPI_MCP_HEADERS",
                        "mcp/notion",
                    ],
                    "env": {"OPENAPI_MCP_HEADERS": str(headers)},
                    "transport": "stdio",
                },
            }
        )
        tools = await client.get_tools()
        agent = create_react_agent(f"openai:{MODEL_NAME}", tools)

        print(f"Processing query: '{query}'")
        print("Connecting to MLflow MCP server...")

        messages = [SystemMessage(content=system_prompt), HumanMessage(content=query)]

        logger.info("Processing query through agent...")
        print("Thinking...")

        agent_response = await agent.ainvoke({"messages": messages})

        logger.info("Query processing complete")
        return agent_response

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}


def main():
    """Main function to parse arguments and run the query processing."""
    parser = argparse.ArgumentParser(
        description="Query MLflow using natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python mlflow_client.py "List all models in my MLflow registry"
          python mlflow_client.py "List all experiments in MLflow registry"
          python mlflow_client.py "Give me details about iris-model"
          python mlflow_client.py "Give me system info"
        """),
    )

    # Add arguments
    parser.add_argument("query", type=str, help="The natural language query to process")

    args = parser.parse_args()

    try:
        # Run the query processing with error handling
        result = asyncio.run(process_query(args.query))

        print("\n=== Results ===\n")

        # Beautify the output
        if isinstance(result, dict) and "error" in result:
            print(f"❌ Error: {result['error']}")
        elif hasattr(result, "get") and result.get("messages"):
            # Extract the final AI response
            messages = result["messages"]
            final_message = None

            # Find the last AI message with actual content
            for msg in reversed(messages):
                if (
                    hasattr(msg, "content")
                    and msg.content
                    and not hasattr(msg, "tool_calls")
                ):
                    final_message = msg
                    break

            if final_message:
                print("🤖 Assistant Response:")
                print("-" * 50)
                print(final_message.content)
            else:
                print("✅ Query processed successfully!")
                # If no final message, show tool results or basic info
                tool_messages = [msg for msg in messages if hasattr(msg, "name")]
                if tool_messages:
                    print("\n📊 Tool Results:")
                    for tool_msg in tool_messages[-3:]:  # Show last 3 tool results
                        print(
                            f"  • {getattr(tool_msg, 'name', 'Tool')}: {tool_msg.content[:200]}..."
                        )
        else:
            # Fallback to formatted JSON output
            import json

            try:
                if hasattr(result, "__dict__"):
                    formatted_result = json.dumps(
                        result.__dict__, indent=2, default=str
                    )
                else:
                    formatted_result = json.dumps(result, indent=2, default=str)
                print(formatted_result)
            except Exception as e:
                print(f"Error formatting result: {str(e)}")
                print(str(result))

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError processing query: {str(e)}")
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
