"""Common utilities."""

import functools
from typing import Any


def rsetattr(obj: Any, attr: str, val: Any) -> None:
    """Set nested attribute of an object."""
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj: Any, attr: str, *args: Any) -> Any:
    """Get nested attribute of an object."""

    def _getattr(obj: Any, attr: str) -> Any:
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))
