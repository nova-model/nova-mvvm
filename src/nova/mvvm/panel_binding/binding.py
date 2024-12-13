"""Binding module for the Panel framework."""

import inspect
from typing import Any

import param

from .._internal.utils import rgetattr, rsetattr
from ..interface import BindingInterface


def is_parameterized(var: Any) -> bool:
    return isinstance(var, param.Parameterized)


def is_callable(var: Any) -> bool:
    return inspect.isfunction(var) or inspect.ismethod(var)


class Communicator:
    """Communicator class, that provides methods required for binding to communicate between ViewModel and View."""

    def __init__(
        self,
        viewmodel_linked_object: Any = None,
        linked_object_attributes: Any = None,
        callback_after_update: Any = None,
    ) -> None:
        self.viewmodel_linked_object = viewmodel_linked_object
        self.linked_object_attributes = linked_object_attributes
        self.callback_after_update = callback_after_update

        self._set_linked_object_attributes(linked_object_attributes, viewmodel_linked_object)

        self.connection: Any = None
        self.param_connect: Any = None
        self.linked_object_parameterized: Any = None

    def _set_linked_object_attributes(self, linked_object_attributes: Any, viewmodel_linked_object: Any) -> None:
        self.linked_object_attributes = None
        if viewmodel_linked_object and not is_callable(viewmodel_linked_object):
            if not linked_object_attributes and not isinstance(viewmodel_linked_object, dict):
                self.linked_object_attributes = {
                    k: v for k, v in viewmodel_linked_object.__dict__.items() if not k.startswith("_")
                }
            elif not linked_object_attributes and isinstance(viewmodel_linked_object, dict):
                self.linked_object_attributes = viewmodel_linked_object
            else:
                self.linked_object_attributes = linked_object_attributes

    # connector can be a dictionary, function, or parameterized object
    def connect(self, connector: Any = None, param_connect: Any = None) -> Any:
        if is_parameterized(connector):
            self.connection = connector
            self.param_connect = param_connect

        elif is_callable(connector):
            self.connection = connector
            return self.get_callback()

        # Register an observer on a parameterized object with specified parameters to
        # watch and call the update function on a single parameter
        if self.viewmodel_linked_object:
            # Connection on the View side should be a dictionary which has a key with string
            # specifying the attribute name in the viewmodel linked
            # the value should be a tuple with this format (parameterized_object, 'parameter', [optional,observers])
            if self.linked_object_attributes and isinstance(connector, dict):
                for attribute_name, connection in connector.items():
                    if attribute_name in self.linked_object_attributes:
                        if not isinstance(connection, tuple) or len(connection) < 2:
                            raise ValueError(f"Expected tuple with at least two elements for {attribute_name}")
                        # creates a watcher on the parameterized object, and uses a specific
                        # parameter of the object to get and set values from
                        if len(connection) > 2:
                            param_observable = connection[2]
                        else:
                            param_observable = connection[1]
                        try:
                            self.connection = connector
                            parameterized = connection[0]
                            param_connector = connection[1]

                            if is_parameterized(parameterized):
                                parameterized.param.watch(
                                    lambda event,
                                    key=attribute_name,
                                    parameter=param_connector: self._update_in_viewmodel(
                                        events=event, key=key, parameter=parameter
                                    ),
                                    param_observable,
                                )
                            else:
                                raise Exception(
                                    f"Cannot create observer for attribute: "
                                    f"{attribute_name} and parameter {param_connector}"
                                )
                        except Exception:
                            raise Exception("Cannot connect", attribute_name) from None

    # Update the viewmodel based on the event triggered or the provided value
    # event parameter is expected but will default to the value parameter if not
    def _update_in_viewmodel(self, events: Any = None, key: str = "", value: Any = None, parameter: Any = None) -> None:
        # Checks to see if the event triggered is the correct event that was specified for the connection
        if events:
            if events.name == parameter:
                value = events.new
            else:
                if self.callback_after_update:
                    self.callback_after_update(key)
                return

        if not value:
            raise Exception("Could not update viewmodel due to invalid value")

        if self.viewmodel_linked_object:
            if self.linked_object_attributes and key in self.linked_object_attributes:
                if not isinstance(self.viewmodel_linked_object, dict):
                    rsetattr(self.viewmodel_linked_object, key, value)
                else:
                    self.viewmodel_linked_object.update({key: value})
            elif is_callable(self.viewmodel_linked_object):
                self.viewmodel_linked_object(value)
            else:
                raise Exception("cannot update", self.viewmodel_linked_object)

        if self.callback_after_update:
            self.callback_after_update(key)

    # Return the update function as a callback
    def get_callback(self) -> Any:
        return self._update_in_viewmodel

    # Update the view based on the provided value
    def update_in_view(self, value: Any) -> None:
        if is_callable(self.connection):
            self.connection(value)
        elif self.viewmodel_linked_object:
            if self.linked_object_attributes:
                for attribute_name in self.linked_object_attributes:
                    if not isinstance(self.viewmodel_linked_object, dict):
                        value_to_change = rgetattr(value, attribute_name)
                    else:
                        value_to_change = self.viewmodel_linked_object[attribute_name]
                    widget, param = self.connection.get(attribute_name, (None, None))[:2]
                    if widget and param:
                        rsetattr(widget, param, value_to_change)
            elif is_callable(self.viewmodel_linked_object):
                self.viewmodel_linked_object(value)
        else:
            rsetattr(self.connection, self.param_connect, value)

        return value


class PanelBinding(BindingInterface):
    """Binding Interface implementation for Panel."""

    def new_bind(
        self, linked_object: Any = None, linked_object_arguments: Any = None, callback_after_update: Any = None
    ) -> Any:
        # each new_bind returns an object that can be used to bind a ViewModel/Model variable
        # with a corresponding GUI framework element
        # for Trame we use state to trigger GUI update and linked_object to trigger ViewModel/Model update
        return Communicator(linked_object, linked_object_arguments, callback_after_update)
