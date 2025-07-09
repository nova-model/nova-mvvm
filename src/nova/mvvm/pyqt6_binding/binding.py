"""Binding module for PyQt framework."""

from typing import Any, Callable

from PyQt6.QtCore import QObject, QThreadPool, pyqtSignal  # type: ignore
from typing_extensions import override

from .._internal.pyqt_communicator import PyQtCommunicator
from ..interface import BindingInterface, Worker
from .pyqt6_worker import PyQt6Worker


class PyQtObject(QObject):
    """PyQt object class."""

    signal = pyqtSignal(object)


class ThreadPool(QThreadPool):
    """ThreadPool class."""

    def __init__(self) -> None:
        super().__init__()


class PyQt6Binding(BindingInterface):
    """Binding Interface implementation for PyQt."""

    def __init__(self) -> None:
        self.thread_pool = ThreadPool()

    def new_bind(
        self, linked_object: Any = None, linked_object_arguments: Any = None, callback_after_update: Any = None
    ) -> Any:
        """Each new_bind returns an object that can be used to bind a ViewModel/Model variable.

        For PyQt we use pyqtSignal to trigger GU
        I update and linked_object to trigger ViewModel/Model update
        """
        return PyQtCommunicator(PyQtObject, linked_object, linked_object_arguments, callback_after_update)

    @override
    def new_worker(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> Worker:
        return PyQt6Worker(self.thread_pool, task, *args, **kwargs)
