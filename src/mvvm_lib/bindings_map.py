"""Module for bindings map ant it's utils."""

from typing import Any, Dict

from pydantic import BaseModel

from mvvm_lib.utils import rget_list_of_fields

bindings_map: Dict[str, Any] = {}


def update_bindings_map(source: Any, value: Any) -> None:
    #    if isinstance(source, BaseModel):
    if issubclass(type(source), BaseModel):
        fields = rget_list_of_fields(source)
        for field in fields:
            bindings_map[field] = value
