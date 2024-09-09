import asyncio
import inspect

from ..interface import BindingInterface, rsetattr, rgetattr


def is_async():
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def is_callable(var):
    return inspect.isfunction(var) or inspect.ismethod(var)


class Communicator:
    def __init__(self, state, viewmodel_linked_object=None, linked_object_attributes=None,
                 callback_after_update=None):
        self.state = state
        self.viewmodel_linked_object = viewmodel_linked_object

        self._set_linked_object_attributes(linked_object_attributes, viewmodel_linked_object)

        self.connection = None
        self.viewmodel_callback_after_update = callback_after_update

    def _set_linked_object_attributes(self, linked_object_attributes, viewmodel_linked_object):
        self.linked_object_attributes = None
        if (viewmodel_linked_object and
                not isinstance(viewmodel_linked_object, dict) and
                not is_callable(viewmodel_linked_object)):
            if not linked_object_attributes:
                self.linked_object_attributes = {k: v for k, v in viewmodel_linked_object.__dict__.items() if
                                                 not k.startswith("_")}
            else:
                self.linked_object_attributes = linked_object_attributes

    def connect(self, connector=None):
        # connect should be called from View side to connect a
        # GUI element (via it's name in Trame state object)
        # and a linked_object (passed during bind creation from ViewModel side)
        if is_callable(connector):
            self.connection = CallBackConnection(self, connector)
        else:
            self.connection = StateConnection(self, connector)
        return self.connection.get_callback()

    def update_in_view(self, value):
        self.connection.update_in_view(value)


class CallBackConnection:
    def __init__(self, communicator: Communicator, callback):
        self.callback = callback
        self.communicator = communicator
        self.viewmodel_linked_object = communicator.viewmodel_linked_object
        self.viewmodel_callback_after_update = communicator.viewmodel_callback_after_update
        self.linked_object_attributes = communicator.linked_object_attributes

    def _update_viewmodel_callback(self, value, key=None):
        if isinstance(self.viewmodel_linked_object, dict):
            if key == None:
                self.viewmodel_linked_object.update(value)
            else:
                self.viewmodel_linked_object.update({key: value})
        elif is_callable(self.viewmodel_linked_object):
            self.viewmodel_linked_object(value)
        elif isinstance(self.viewmodel_linked_object, object):
            if key == None:
                raise Exception("Cannot update", self.viewmodel_linked_object, ": key is missing")
            rsetattr(self.viewmodel_linked_object, key, value)
        else:
            raise Exception("Cannot update", self.viewmodel_linked_object)

        if self.viewmodel_callback_after_update:
            self.viewmodel_callback_after_update(key)

    def update_in_view(self, value):
        self.callback(value)

    def get_callback(self):
        return self._update_viewmodel_callback


class StateConnection:
    def __init__(self, communicator: Communicator, state_variable_name):
        self.state_variable_name = state_variable_name
        self.communicator = communicator
        self.state = communicator.state
        self.viewmodel_linked_object = communicator.viewmodel_linked_object
        self.viewmodel_callback_after_update = communicator.viewmodel_callback_after_update
        self.linked_object_attributes = communicator.linked_object_attributes
        self._connect()

    def _on_state_update(self, attribute_name, name_in_state):
        def update(**kwargs):
            rsetattr(self.viewmodel_linked_object, attribute_name, self.state[name_in_state])
            if self.viewmodel_callback_after_update:
                self.viewmodel_callback_after_update(attribute_name)

        return update

    def _set_variable_in_state(self, name_in_state, value):
        if is_async():
            with self.state:
                self.state[name_in_state] = value
                self.state.dirty(name_in_state)
        else:
            self.state[name_in_state] = value
            self.state.dirty(name_in_state)

    def _get_name_in_state(self, attribute_name):
        if self.state_variable_name:
            name_in_state = f"{self.state_variable_name}_{attribute_name.replace('.', '_')}"
        else:
            name_in_state = attribute_name.replace('.', '_')
        return name_in_state

    def _connect(self):
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
            else:
                @self.state.change(state_variable_name)
                def update_viewmodel_callback(**kwargs):
                    if isinstance(self.viewmodel_linked_object, dict):
                        self.viewmodel_linked_object.update(kwargs[state_variable_name])
                    elif is_callable(self.viewmodel_linked_object):
                        self.viewmodel_linked_object(kwargs[state_variable_name])
                    else:
                        raise Exception("cannot update", self.viewmodel_linked_object)
                    if self.viewmodel_callback_after_update:
                        self.viewmodel_callback_after_update(state_variable_name)

    def update_in_view(self, value):
        if self.linked_object_attributes:
            for attribute_name in self.linked_object_attributes:
                name_in_state = self._get_name_in_state(attribute_name)
                value_to_change = rgetattr(value, attribute_name)
                self._set_variable_in_state(name_in_state, value_to_change)
        else:
            self._set_variable_in_state(self.state_variable_name, value)

    def get_callback(self):
        return None


class TrameBinding(BindingInterface):
    def __init__(self, state):
        self._state = state

    def new_bind(self, linked_object=None, linked_object_arguments=None, callback_after_update=None):
        # each new_bind returns an object that can be used to bind a ViewModel/Model variable
        # with a corresponding GUI framework element
        # for Trame we use state to trigger GUI update and linked_object to trigger ViewModel/Model update
        return Communicator(self._state, linked_object, linked_object_arguments, callback_after_update)
