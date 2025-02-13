"""Binding module for PyQt5 framework."""

import inspect
from typing import Any

from PyQt5.QtCore import QObject, pyqtSignal

from .._internal.pyqt_communicator import PyQtCommunicator
from ..interface import BindingInterface


def is_callable(var: Any) -> bool:
    return inspect.isfunction(var) or inspect.ismethod(var)


class PyQtObject(QObject):
    """PyQt object class."""

    signal = pyqtSignal(object)


class PyQt5Binding(BindingInterface):
    """Binding Interface implementation for PyQt."""

    def new_bind(
        self, linked_object: Any = None, linked_object_arguments: Any = None, callback_after_update: Any = None
    ) -> Any:
        """Each new_bind returns an object that can be used to bind a ViewModel/Model variable.

        For PyQt we use pyqtSignal to trigger GU
        I update and linked_object to trigger ViewModel/Model update
        """
        return PyQtCommunicator(PyQtObject, linked_object, linked_object_arguments, callback_after_update)
