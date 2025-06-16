import importlib
from typing import Any
import yaml


class YAMLUtils:
    @staticmethod
    def dummy_constructor(loader, node):
        return lambda state: None

    @staticmethod
    def import_class(path: str) -> Any:
        """
        Import a class from a string path.

        Args:
            path: Path in format "module.submodule.ClassName"

        Returns:
            The class object
        """
        try:
            module_path, class_name = path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not import {path}: {str(e)}")

    @classmethod
    def register_constructors(cls):
        """Register built-in YAML constructors for common cases"""
        yaml.SafeLoader.add_constructor("!dummy", cls.dummy_constructor)

    @staticmethod
    def safe_load(stream):
        YAMLUtils.register_constructors()
        return yaml.safe_load(stream)

    @staticmethod
    def safe_dump(data, stream=None, **kwargs):
        """Safe dump YAML data"""
        return yaml.safe_dump(data, stream=stream, **kwargs)
