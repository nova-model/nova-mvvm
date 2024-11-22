"""Common utilities."""

import re
from typing import Any


def normalize_field_name(field: str) -> str:
    return field.replace(".", "_").replace("[", "_").replace("]", "")


#            .replace("_length", "n"))


def list_has_objects(v: list) -> bool:
    for elem in v:
        if isinstance(elem, list):
            return list_has_objects(elem)
        elif hasattr(elem, "__dict__"):
            return True
    return False


def rget_list_of_fields(obj: Any, prefix: str = "") -> Any:
    if not hasattr(obj, "__dict__"):
        return [prefix]
    attributes = []
    for k, v in obj.__dict__.items():
        if not k.startswith("_"):  # Ignore private attributes
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, list) and list_has_objects(v):
                for i, elem in enumerate(v):
                    attributes.extend(rget_list_of_fields(elem, prefix=f"{full_key}[{i}]"))
            elif hasattr(v, "__dict__"):  # Check if the value is another object with attributes
                attributes.extend(rget_list_of_fields(v, prefix=full_key))
            else:
                attributes.append(full_key)
    return attributes


def rgetattr(obj: Any, attr: str) -> Any:
    fields = attr.split(".")
    for field in fields:
        base = field.split("[")[0]
        obj = getattr(obj, base)
        indices = re.findall(r"\[(\d+)\]", field)
        indices = [int(num) for num in indices]
        for index in indices:
            obj = obj[index]
    return obj


def rsetattr(obj: Any, attr: str, val: Any) -> Any:
    pre, _, post = attr.rpartition(".")
    if pre:
        obj = rgetattr(obj, pre)
    if "[" in post:
        indices = re.findall(r"\[(\d+)\]", post)
        indices = [int(num) for num in indices]
        for i, index in enumerate(indices):
            if i == len(indices) - 1:
                obj[index] = val
            else:
                obj = obj[index]
    else:
        setattr(obj, post, val)
