"""Binding module for PyQt6 framework."""

from typing import Any, Optional

from ..utils import rsetattr

try:
    from PyQt6.QtCore import QObject, pyqtSignal
except Exception:
    print("PyQt6 is missing. You could install 'py-mvvm[pyqt6]' to fix it")
    exit(1)

import inspect

from ..interface import BindingInterface


def is_callable(var: Any) -> bool:
    return inspect.isfunction(var) or inspect.ismethod(var)


class Communicator(QObject):
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

    def _update_viewmodel_callback(self, key: Optional[str] = None, value: Any = None) -> None:
        if isinstance(self.viewmodel_linked_object, dict):
            self.viewmodel_linked_object.update({key: value})
        elif is_callable(self.viewmodel_linked_object):
            self.viewmodel_linked_object(value)
        elif isinstance(self.viewmodel_linked_object, object):
            rsetattr(self.viewmodel_linked_object, key or "", value)
        else:
            raise Exception("Cannot update", self.viewmodel_linked_object)

        if self.callback_after_update:
            self.callback_after_update(key)

    def connect(self, *args: Any, **kwargs: Any) -> Any:
        # connect should be called from the View side to connect a
        # GUI element (via a function to change GUI element that is passed to the connect call)
        # and a linked_object (passed during bind creation from ViewModel side)
        self.signal.connect(*args, **kwargs)
        if self.viewmodel_linked_object:
            return self._update_viewmodel_callback
        else:
            return None

    def update_in_view(self, *args: Any, **kwargs: Any) -> Any:
        """Update a View (GUI) when called by a ViewModel."""
        return self.signal.emit(*args, **kwargs)


class PyQtBinding(BindingInterface):
    """Binding Interface implementation for PyQt6."""

    def new_bind(
        self, linked_object: Any = None, linked_object_arguments: Any = None, callback_after_update: Any = None
    ) -> Any:
        """Each new_bind returns an object that can be used to bind a ViewModel/Model variable.

        For PyQt we use pyqtSignal to trigger GU
        I update and linked_object to trigger ViewModel/Model update
        """
        return Communicator(linked_object, linked_object_arguments, callback_after_update)
