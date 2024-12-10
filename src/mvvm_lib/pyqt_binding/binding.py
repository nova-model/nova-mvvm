"""Binding module for PyQt framework."""

import os
from typing import Any, Callable, Optional

from pydantic import BaseModel

from ..bindings_map import update_bindings_map
from ..utils import rsetattr

if os.environ.get("QT_API", None) == "pyqt5":
    try:
        from PyQt5.QtCore import QObject, pyqtSignal
    except Exception:
        print("PyQt5 is missing. You should install 'mvvm-lib[pyqt5]' to fix it")
        exit(1)
else:
    try:
        from PyQt6.QtCore import QObject, pyqtSignal  # type: ignore
    except Exception:
        print("PyQt6 is missing. You should install 'mvvm-lib[pyqt6]' to fix it")
        exit(1)

import inspect

from ..interface import BindingInterface


def is_callable(var: Any) -> bool:
    return inspect.isfunction(var) or inspect.ismethod(var)


class PyQtCommunicator(QObject):
    """Communicator class, that provides methods required for binding to communicate between ViewModel and View."""

    signal = pyqtSignal(object)

    def __init__(
        self,
        viewmodel_linked_object: Any = None,
        linked_object_attributes: Any = None,
        callback_after_update: Any = None,
    ) -> None:
        super().__init__()
        self.viewmodel_linked_object = viewmodel_linked_object
        self.linked_object_attributes = linked_object_attributes
        self.callback_after_update = callback_after_update
        self.prefix = ""

    def _update_viewmodel_callback(self, key: Optional[str] = None, value: Any = None) -> None:
        if issubclass(type(self.viewmodel_linked_object), BaseModel):
            model = self.viewmodel_linked_object.copy(deep=True)
            if self.prefix and key:
                key = key.removeprefix(f"{self.prefix}.")
            rsetattr(model, key or "", value)
            try:
                new_model = model.__class__(**model.model_dump(warnings=False))
                for f, v in new_model:
                    setattr(self.viewmodel_linked_object, f, v)
            except Exception:
                pass
        elif isinstance(self.viewmodel_linked_object, dict):
            self.viewmodel_linked_object.update({key: value})
        elif is_callable(self.viewmodel_linked_object):
            self.viewmodel_linked_object(value)
        elif isinstance(self.viewmodel_linked_object, object):
            rsetattr(self.viewmodel_linked_object, key or "", value)
        else:
            raise Exception("Cannot update", self.viewmodel_linked_object)

        if self.callback_after_update:
            self.callback_after_update(key)

    def connect(self, name: str, callback: Callable) -> Any:
        # connect should be called from the View side to connect a
        # GUI element (via a function to change GUI element that is passed to the connect call)
        # and a linked_object (passed during bind creation from ViewModel side)
        update_bindings_map(name, self)
        self.prefix = name
        self.signal.connect(callback)
        if self.viewmodel_linked_object:
            return self._update_viewmodel_callback
        else:
            return None

    def update_in_view(self, value: Any) -> Any:
        """Update a View (GUI) when called by a ViewModel."""
        return self.signal.emit(value)


class PyQtBinding(BindingInterface):
    """Binding Interface implementation for PyQt."""

    def new_bind(
        self, linked_object: Any = None, linked_object_arguments: Any = None, callback_after_update: Any = None
    ) -> Any:
        """Each new_bind returns an object that can be used to bind a ViewModel/Model variable.

        For PyQt we use pyqtSignal to trigger GU
        I update and linked_object to trigger ViewModel/Model update
        """
        return PyQtCommunicator(linked_object, linked_object_arguments, callback_after_update)
