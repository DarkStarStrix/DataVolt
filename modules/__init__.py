"""
Consolidated modules package exposing domain-specific scripts and data helpers.
Each subpackage follows the `modules/<name>/[scripts|data]` convention.
"""

from importlib import import_module
from pathlib import Path
from typing import Dict

__all__ = [
    "available_modules",
    "load_module_scripts",
]


def available_modules() -> Dict[str, Path]:
    """Return mapping of module name to its base directory."""
    base = Path(__file__).resolve().parent
    return {child.name: child for child in base.iterdir() if child.is_dir()}


def load_module_scripts(name: str):
    """
    Dynamically import the scripts package for a given module.

    Args:
        name: Name of the module directory (e.g., ``'etl'``).

    Returns:
        Imported module object.
    """
    return import_module(f"modules.{name}.scripts")
