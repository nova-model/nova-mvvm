"""Binding module for PyQt framework."""

from typing import Any

from PyQt6.QtCore import QObject, pyqtSignal  # type: ignore

from .._internal.pyqt_communicator import PyQtCommunicator
from ..interface import BindingInterface


class PyQtObject(QObject):
    """PyQt object class."""

    signal = pyqtSignal(object)


class PyQt6Binding(BindingInterface):
    """Binding Interface implementation for PyQt."""

    def new_bind(
        self, linked_object: Any = None, linked_object_arguments: Any = None, callback_after_update: Any = None
    ) -> Any:
        """Each new_bind returns an object that can be used to bind a ViewModel/Model variable.

        For PyQt we use pyqtSignal to trigger GU
        I update and linked_object to trigger ViewModel/Model update
        """
        return PyQtCommunicator(PyQtObject, linked_object, linked_object_arguments, callback_after_update)
