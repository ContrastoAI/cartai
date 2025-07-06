import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from cartai.mcps.exceptions import MCPInitializationError
from cartai.utils.yaml_utils import YAMLUtils

logger = logging.getLogger(__name__)

load_dotenv()


class MCPRegistry:
    """
    Simple MCP configuration loader.

    Loads MCP configurations from YAML and provides them in the format
    expected by MultiServerMCPClient.
    """

    def __init__(
        self,
        mcp_config_path: Path | None = None,
        environment: str = "development",
    ):
        self.environment = environment
        self.mcp_config_path = mcp_config_path or Path(
            "cartai/mcps/configs/mcp_configs.yaml"
        )

    def get_client_config(self) -> dict:
        """
        Load MCP configurations and return in MultiServerMCPClient format

        Returns:
            dict: Configuration dictionary ready for MultiServerMCPClient
        """
        logger.info(f"Loading MCP configurations for environment: {self.environment}")

        try:
            config = self._load_config()
            env_config = config.get("environments", {}).get(self.environment, {})
            mcps_config = env_config.get("mcps", {})

            if not mcps_config:
                logger.warning(
                    f"No MCP configurations found for environment: {self.environment}"
                )
                return {}
            # Convert to MultiServerMCPClient format
            client_config = {}
            for name, mcp_data in mcps_config.items():
                if mcp_data.get("enabled", True):
                    client_config[name] = self._convert_to_client_config(mcp_data)
                    logger.debug(f"Added MCP config: {name}")

            logger.info(f"Loaded {len(client_config)} MCP configurations")
            return client_config

        except Exception as e:
            logger.error(f"Failed to load MCP configurations: {str(e)}")
            raise MCPInitializationError(f"MCP configuration loading failed: {str(e)}")

    def _load_config(self) -> dict:
        """Load configuration from YAML file with environment variable substitution"""
        if not self.mcp_config_path.exists():
            raise FileNotFoundError(
                f"MCP config file not found: {self.mcp_config_path}"
            )

        with open(self.mcp_config_path, "r", encoding="utf-8") as file:  # type: ignore
            config = YAMLUtils.safe_load(file)

        # Environment variable substitution
        config_str = YAMLUtils.safe_dump(config)
        import re

        config_str = re.sub(
            r"\$\{(\w+)\}", lambda m: os.getenv(m.group(1), ""), config_str
        )
        return YAMLUtils.safe_load(config_str)

    def _convert_to_client_config(self, mcp_data: dict) -> dict:
        """Convert MCP config to MultiServerMCPClient format"""
        client_config = {}

        if "transport" in mcp_data:
            client_config["transport"] = mcp_data["transport"]
        if "url" in mcp_data:
            client_config["url"] = mcp_data["url"]
        if "command" in mcp_data:
            client_config["command"] = mcp_data["command"]
        if "args" in mcp_data:
            client_config["args"] = mcp_data["args"]
        if "env" in mcp_data:
            client_config["env"] = mcp_data["env"]
        if "description" in mcp_data:
            client_config["description"] = mcp_data["description"]

        return client_config

    def get_mcp_description(self, mcp_name: str) -> str | None:
        """
        Get the description for a specific MCP.

        Args:
            mcp_name: Name of the MCP

        Returns:
            str | None: Description of the MCP if available, None otherwise
        """
        config = self.get_client_config()
        if mcp_name in config:
            return config[mcp_name].get("description")
        return None

    def get_all_mcp_descriptions(self) -> dict[str, str]:
        """
        Get descriptions for all available MCPs.

        Returns:
            dict[str, str]: Dictionary mapping MCP names to their descriptions
        """
        config = self.get_client_config()
        return {
            name: mcp_config.get("description", "")
            for name, mcp_config in config.items()
        }

    def get_filtered_client_config(self, mcp_names: list[str]) -> dict:
        """
        Get filtered MCP configuration for specific MCPs.

        Args:
            mcp_names: List of MCP names to include

        Returns:
            Filtered configuration dictionary for MultiServerMCPClient
        """
        full_config = self.get_client_config()

        filtered_config = {}
        for mcp_name in mcp_names:
            if mcp_name in full_config:
                filtered_config[mcp_name] = full_config[mcp_name]
                logger.debug(f"Added MCP '{mcp_name}' to filtered config")
            else:
                logger.warning(f"Requested MCP '{mcp_name}' not found in configuration")

        logger.info(
            f"Created filtered config with {len(filtered_config)} MCPs: {list(filtered_config.keys())}"
        )
        return filtered_config

    def get_available_mcps(self) -> list[str]:
        """Get list of available MCP names from configuration"""
        config = self.get_client_config()
        return list(config.keys())
