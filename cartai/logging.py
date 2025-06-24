import logging
import os
from pathlib import Path
from typing import Dict, Type

from cartai.utils.yaml_utils import YAMLUtils

DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = "INFO"

class LoggerFactory:
    """
    Factory class for creating and managing loggers across the CartAI system.
    
    This class handles:
    - Loading logging configuration from YAML
    - Setting up logging providers (console, file, logfire, etc.)
    - Providing a unified way to get logger instances
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._config = self._load_config()
            self._setup_root_logger()
            self._initialized = True
    
    def _load_config(self) -> Dict:
        """Load logging configuration from YAML file."""
        config_locations = [
            os.environ.get("CARTAI_LOGGING_CONFIG"),  # 1. Environment variable
            "logging_config.yaml",                     # 2. Current directory
            "config/logging_config.yaml",              # 3. Config subdirectory
            Path.home() / ".cartai/config/logging_config.yaml", # 4. User's home directory
            Path(__file__).parent / "config/logging_config.yaml"  # 5. Package directory
        ]
        
        for config_path in config_locations:
            if config_path and Path(config_path).exists():
                try:
                    with open(config_path, "r") as f:
                        return YAMLUtils.safe_load(f)
                except Exception as e:
                    print(f"Warning: Failed to load logging config from {config_path}: {e}")
        
        return {
            "version": 1,
            "formatters": {
                "default": {
                    "format": DEFAULT_LOG_FORMAT
                }
            },
            "handlers": {
                "console": {
                    "class": "StreamHandler",
                    "formatter": "default",
                    "level": DEFAULT_LOG_LEVEL
                }
            },
            "root": {
                "level": DEFAULT_LOG_LEVEL,
                "handlers": ["console"]
            }
        }
    
    def _import_handler_class(self, class_path: str) -> Type:
        """
        Safely import a handler class.
        
        Args:
            class_path: Either a fully qualified class path or a logging handler name
            
        Returns:
            The handler class
        
        Raises:
            ImportError: If the class cannot be imported
        """
        try:
            return YAMLUtils.import_class(class_path)
        except ImportError as e:
            print(f"Warning: Failed to import handler class {class_path}: {e}")
            return logging.StreamHandler
    
    def _setup_root_logger(self):
        """Configure the root logger based on loaded configuration."""
        config = self._config
        
        env = os.environ.get("CARTAI_ENV", "development")
        env_config = config.get("environments", {}).get(env, config)
        
        formatters = {}
        for fmt_name, fmt_config in env_config.get("formatters", {}).items():
            formatter_class = None
            if "class" in fmt_config:
                try:
                    formatter_class = self._import_handler_class(fmt_config["class"])
                except ImportError:
                    print(f"Warning: Failed to import formatter class for {fmt_name}, using default")
            
            if formatter_class:
                formatters[fmt_name] = formatter_class(fmt_config.get("format", DEFAULT_LOG_FORMAT))
            else:
                formatters[fmt_name] = logging.Formatter(fmt_config.get("format", DEFAULT_LOG_FORMAT))
        
        # Set up handlers
        handlers = {}
        for handler_name, handler_config in env_config.get("handlers", {}).items():
            try:
                handler_class_path = handler_config.get("class", "StreamHandler")
                handler_class = self._import_handler_class(handler_class_path)
                
                handler = handler_class()
                
                handler.setLevel(handler_config.get("level", DEFAULT_LOG_LEVEL))
                
                formatter_name = handler_config.get("formatter")
                if formatter_name and formatter_name in formatters:
                    handler.setFormatter(formatters[formatter_name])
                
                for key, value in handler_config.items():
                    if key not in ["class", "formatter", "level"]:
                        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                            env_var = value[2:-1]
                            value = os.environ.get(env_var)
                            if value is None:
                                print(f"Warning: Environment variable {env_var} not set for handler {handler_name}")
                                continue
                        
                        if hasattr(handler, key):
                            setattr(handler, key, value)
                
                handlers[handler_name] = handler
            except Exception as e:
                print(f"Warning: Failed to configure handler {handler_name}: {e}")
                # Add a basic StreamHandler as fallback
                handlers[handler_name] = logging.StreamHandler()
        
        root_config = env_config.get("root", {})
        root_logger = logging.getLogger()
        root_logger.setLevel(root_config.get("level", DEFAULT_LOG_LEVEL))
        
        # remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # add configured handlers
        for handler_name in root_config.get("handlers", []):
            if handler_name in handlers:
                root_logger.addHandler(handlers[handler_name])
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.
        
        Args:
            name: Name for the logger, typically __name__ of the module
            
        Returns:
            logging.Logger: Configured logger instance
        """
        return logging.getLogger(name)


_factory = LoggerFactory()

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    This is the main function that should be used by other modules to get a logger.
    
    Args:
        name: Name for the logger, typically __name__ of the module
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return _factory.get_logger(name) 