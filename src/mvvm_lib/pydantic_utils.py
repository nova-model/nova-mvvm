"""Pydantic utils."""

import logging
import re
from typing import Any

from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo

from mvvm_lib import bindings_map

logger = logging.getLogger(__name__)


def get_nested_pydantic_field(model: BaseModel, field_path: str) -> FieldInfo:
    fields = field_path.split(".")
    current_model: Any = model

    for field in fields:
        if "[" in field:
            base = field.split("[")[0]
            current_model = getattr(current_model, base)
            for _ in range(field.count("[")):
                current_model = current_model[0]
            continue
        if issubclass(type(getattr(current_model, field)), BaseModel):
            current_model = getattr(current_model, field)
        else:
            return current_model.__fields__[field]

    raise Exception(f"Cannot find field {field_path}")


def get_field_info(field_name: str) -> FieldInfo:
    binding = bindings_map.get(field_name, None)
    if not binding:
        raise Exception(f"Cannot find field {field_name}")
    return get_nested_pydantic_field(binding.viewmodel_linked_object, field_name)


def validate_pydantic_parameter(name: str, value: Any, index: int) -> str | None:
    if name not in bindings_map:
        logger.warning(f"cannot find {name} in bindings_map")  # no error, just do not validate for now
        return None
    binding = bindings_map[name]
    current_model = binding.viewmodel_linked_object
    # get list of nested fields (if any) and get the corresponding model
    fields = name.split(".")
    for field in fields[:-1]:
        if "[" in field:
            base = field.split("[")[0]
            indices = re.findall(r"\[(\d+)\]", field)
            indices = [int(num) for num in indices]
            for i in indices:
                current_model = getattr(current_model, base)[i]
        else:
            current_model = getattr(current_model, field)
    final_field = fields[-1]
    # copy model so we do not modify the current one
    model = current_model.copy(deep=True)
    # force set field value
    setattr(model, final_field, value)
    # validate changed model
    try:
        model.__class__(**model.model_dump(warnings=False))
    except ValidationError as e:
        for error in e.errors():
            if (len(error["loc"]) > 0 and final_field in str(error["loc"][0])) or (
                len(error["loc"]) == 0 and e.title == current_model.__class__.__name__
            ):
                return error["msg"]
    return None
