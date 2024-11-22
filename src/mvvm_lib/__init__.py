import importlib.metadata

from .bindings_map import bindings_map

__version__ = importlib.metadata.version(__package__)

__all__ = ["bindings_map"]
