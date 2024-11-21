"""Common utilities."""

import re
from typing import Any


def rgetattr(obj: Any, attr: str) -> Any:
    fields = attr.split(".")
    for field in fields:
        base = field.split("[")[0]
        obj = getattr(obj, base)
        indices = []
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
