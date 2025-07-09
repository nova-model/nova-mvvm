"""Worker module for PyQt5 framework."""

import sys
import traceback
from typing import Any, Callable

from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from typing_extensions import override

from nova.mvvm.interface import Worker


class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    progress = pyqtSignal(str, int)
    result = pyqtSignal(object)


class PyQt5Worker(QRunnable, Worker):
    """Worker class that executes a function with provided arguments in a separate thread."""

    def __init__(self, thread_pool: QThreadPool, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.thread_pool = thread_pool
        self.signals = WorkerSignals()
        self.task = task
        self.args = args
        self.kwargs = kwargs

        self.kwargs["progress"] = self._emit_progress

    @pyqtSlot()
    def run(self) -> None:
        try:
            result = self.task(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

    def _emit_progress(self, message: str, progress: int) -> None:
        self.signals.progress.emit(message, progress)

    @override
    def connect_error(self, callback: Callable[[Any], None]) -> None:
        self.signals.error.connect(callback)

    @override
    def connect_result(self, callback: Callable[[Any], None]) -> None:
        self.signals.result.connect(callback)

    @override
    def connect_finished(self, callback: Callable[[], None]) -> None:
        self.signals.finished.connect(callback)

    @override
    def connect_progress(self, callback: Callable[[str, int], None]) -> None:
        self.signals.progress.connect(callback)

    @override
    def start(self) -> None:
        self.thread_pool.start(self)
