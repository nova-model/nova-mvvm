"""Module for bindings map ant it's utils."""

from typing import Any, Dict

bindings_map: Dict[str, Any] = {}


def update_bindings_map(key: str | None, value: Any) -> None:
    if key:
        bindings_map[key] = value
