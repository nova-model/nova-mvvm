"""Abstract interfaces."""

import functools
from abc import ABC, abstractmethod
from typing import Any


class BindingInterface(ABC):
    """Abstract binding interface."""

    @abstractmethod
    def new_bind(
        self, linked_object: Any = None, linked_object_arguments: Any = None, callback_after_update: Any = None
    ) -> Any:
        raise Exception("Please implement in a concrete class")


def rsetattr(obj: Any, attr: str, val: Any) -> None:
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj: Any, attr: str, *args: Any) -> Any:
    def _getattr(obj: Any, attr: str) -> Any:
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))
