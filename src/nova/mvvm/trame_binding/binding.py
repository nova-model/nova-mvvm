"""Binding module for Trame framework."""

import asyncio
import inspect
import json
from typing import Any, Callable, Optional, Union, cast

from pydantic import BaseModel
from trame_server.state import State
from typing_extensions import override

from ..bindings_map import update_bindings_map
from ..interface import (
    BindingInterface,
    CallbackAfterUpdateType,
    Communicator,
    ConnectCallbackType,
    LinkedObjectAttributesType,
    LinkedObjectType,
)
from ..utils import normalize_field_name, rget_list_of_fields, rgetattr, rsetattr


def is_async() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def is_callable(var: Any) -> bool:
    return inspect.isfunction(var) or inspect.ismethod(var)


class TrameCommunicator(Communicator):
    """Communicator implementation for Trame."""

    def __init__(
        self,
        state: State,
        viewmodel_linked_object: LinkedObjectType = None,
        linked_object_attributes: LinkedObjectAttributesType = None,
        callback_after_update: CallbackAfterUpdateType = None,
    ) -> None:
        self.state = state
        self.viewmodel_linked_object = viewmodel_linked_object
        self._set_linked_object_attributes(linked_object_attributes, viewmodel_linked_object)
        self.viewmodel_callback_after_update = callback_after_update
        self.connection: Union[CallBackConnection, StateConnection]

    def _set_linked_object_attributes(
        self, linked_object_attributes: LinkedObjectAttributesType, viewmodel_linked_object: LinkedObjectType
    ) -> None:
        self.linked_object_attributes: LinkedObjectAttributesType = None
        if (
            viewmodel_linked_object
            and not isinstance(viewmodel_linked_object, dict)
            and not issubclass(type(viewmodel_linked_object), BaseModel)
            and not is_callable(viewmodel_linked_object)
        ):
            if not linked_object_attributes:
                self.linked_object_attributes = rget_list_of_fields(viewmodel_linked_object)
            else:
                self.linked_object_attributes = linked_object_attributes

    @override
    def connect(self, connector: Any = None) -> ConnectCallbackType:
        if is_callable(connector):
            self.connection = CallBackConnection(self, connector)
        else:
            connector = str(connector) if connector else None
            update_bindings_map(connector, self)
            self.connection = StateConnection(self, connector)
        return self.connection.get_callback()

    def update_in_view(self, value: Any) -> None:
        self.connection.update_in_view(value)


class CallBackConnection:
    """Connection that uses callback."""

    def __init__(self, communicator: TrameCommunicator, callback: Callable[[Any], None]) -> None:
        self.callback = callback
        self.communicator = communicator
        self.viewmodel_linked_object = communicator.viewmodel_linked_object
        self.viewmodel_callback_after_update = communicator.viewmodel_callback_after_update
        self.linked_object_attributes = communicator.linked_object_attributes

    def _update_viewmodel_callback(self, value: Any, key: Optional[str] = None) -> None:
        if self.viewmodel_linked_object and issubclass(type(self.viewmodel_linked_object), BaseModel):
            model = self.viewmodel_linked_object.copy(deep=True)
            rsetattr(model, key or "", value)
            try:
                new_model = model.__class__(**model.model_dump(warnings=False))
                for f, v in new_model:
                    setattr(self.viewmodel_linked_object, f, v)
            except Exception:
                pass
        elif isinstance(self.viewmodel_linked_object, dict):
            if not key:
                self.viewmodel_linked_object.update(value)
            else:
                self.viewmodel_linked_object.update({key: value})
        elif is_callable(self.viewmodel_linked_object):
            cast(Callable, self.viewmodel_linked_object)(value)
        elif isinstance(self.viewmodel_linked_object, object):
            if not key:
                raise Exception("Cannot update", self.viewmodel_linked_object, ": key is missing")
            rsetattr(self.viewmodel_linked_object, key, value)
        else:
            raise Exception("Cannot update", self.viewmodel_linked_object)

        if self.viewmodel_callback_after_update:
            self.viewmodel_callback_after_update(key)

    def update_in_view(self, value: Any) -> None:
        self.callback(value)

    def get_callback(self) -> ConnectCallbackType:
        return self._update_viewmodel_callback


class StateConnection:
    """Connection that uses a state variable."""

    def __init__(self, communicator: TrameCommunicator, state_variable_name: Optional[str]) -> None:
        self.state_variable_name = state_variable_name
        self.communicator = communicator
        self.state = communicator.state
        self.viewmodel_linked_object = communicator.viewmodel_linked_object
        self.viewmodel_callback_after_update = communicator.viewmodel_callback_after_update
        self.linked_object_attributes = communicator.linked_object_attributes
        self._connect()

    async def _handle_callback(self, arg: str) -> None:
        if self.viewmodel_callback_after_update:
            if inspect.iscoroutinefunction(self.viewmodel_callback_after_update):
                await self.viewmodel_callback_after_update(arg)
            else:
                self.viewmodel_callback_after_update(arg)

    def _on_state_update(self, attribute_name: str, name_in_state: str) -> Callable:
        async def update(**_kwargs: Any) -> None:
            rsetattr(self.viewmodel_linked_object, attribute_name, self.state[name_in_state])
            await self._handle_callback(attribute_name)

        return update

    def _set_variable_in_state(self, name_in_state: str, value: Any) -> None:
        if is_async():
            with self.state:
                self.state[name_in_state] = value
                self.state.dirty(name_in_state)
        else:
            self.state[name_in_state] = value
            self.state.dirty(name_in_state)

    def _get_name_in_state(self, attribute_name: str) -> str:
        name_in_state = normalize_field_name(attribute_name)
        if self.state_variable_name:
            name_in_state = f"{self.state_variable_name}_{name_in_state}"
        return name_in_state

    def _connect(self) -> None:
        state_variable_name = self.state_variable_name
        # we need to make sure state variable exists on connect since if it does not - Trame will not monitor it
        if state_variable_name:
            self.state.setdefault(state_variable_name, None)
        for attribute_name in self.linked_object_attributes or []:
            name_in_state = self._get_name_in_state(attribute_name)
            self.state.setdefault(name_in_state, None)

        # this updates ViewModel on state change
        if self.viewmodel_linked_object:
            if self.linked_object_attributes:
                for attribute_name in self.linked_object_attributes:
                    name_in_state = self._get_name_in_state(attribute_name)
                    f = self._on_state_update(attribute_name, name_in_state)
                    self.state.change(name_in_state)(f)
            elif state_variable_name:

                @self.state.change(state_variable_name)
                async def update_viewmodel_callback(**kwargs: dict) -> None:
                    updated = True
                    if self.viewmodel_linked_object and issubclass(type(self.viewmodel_linked_object), BaseModel):
                        json_str = json.dumps(kwargs[state_variable_name])
                        try:
                            model = self.viewmodel_linked_object.model_validate_json(json_str)
                            if model != self.viewmodel_linked_object:
                                for field, value in model:
                                    setattr(self.viewmodel_linked_object, field, value)
                            else:
                                updated = False
                        except Exception:
                            updated = False
                    elif isinstance(self.viewmodel_linked_object, dict):
                        self.viewmodel_linked_object.update(kwargs[state_variable_name])
                    elif is_callable(self.viewmodel_linked_object):
                        cast(Callable, self.viewmodel_linked_object)(kwargs[state_variable_name])
                    else:
                        raise Exception("cannot update", self.viewmodel_linked_object)
                    if updated:
                        await self._handle_callback(state_variable_name)

    def update_in_view(self, value: Any) -> None:
        if issubclass(type(value), BaseModel):
            value = value.model_dump()
        if self.linked_object_attributes:
            for attribute_name in self.linked_object_attributes:
                name_in_state = self._get_name_in_state(attribute_name)
                value_to_change = rgetattr(value, attribute_name)
                self._set_variable_in_state(name_in_state, value_to_change)
        elif self.state_variable_name:
            self._set_variable_in_state(self.state_variable_name, value)

    def get_callback(self) -> ConnectCallbackType:
        return None


class TrameBinding(BindingInterface):
    """Binding Interface implementation for Trame."""

    def __init__(self, state: State) -> None:
        self._state = state

    @override
    def new_bind(
        self,
        linked_object: LinkedObjectType = None,
        linked_object_arguments: LinkedObjectAttributesType = None,
        callback_after_update: CallbackAfterUpdateType = None,
    ) -> TrameCommunicator:
        return TrameCommunicator(self._state, linked_object, linked_object_arguments, callback_after_update)
