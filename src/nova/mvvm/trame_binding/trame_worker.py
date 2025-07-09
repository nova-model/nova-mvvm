"""Worker module for Trame framework."""

import asyncio
import inspect
import sys
import threading
import traceback
from typing import Any, Awaitable, Callable, Optional, Tuple, Union

from typing_extensions import override

from nova.mvvm.interface import Worker

ProgressCallback = Union[Callable[[str, int], None], Callable[[str, int], Awaitable[None]]]


def is_async() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


class TrameWorker(Worker):
    """Worker class for Trame framework."""

    def __init__(self, task: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.kwargs["progress"] = self.set_progress

        # State to be monitored
        self._progress_message: Optional[str] = None
        self._progress_value: Optional[int] = None
        self._result: Optional[Any] = None
        self._error: Optional[Any] = None

        self._progress_lock = threading.Lock()
        self._done = threading.Event()

        # Callbacks
        self._on_result: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._on_finished: Optional[Callable] = None
        self._on_progress: Optional[Callable] = None

        # Worker thread
        self._thread = threading.Thread(target=self._run_task)

    def set_progress(self, message: str, value: int) -> None:
        with self._progress_lock:
            self._progress_message = message
            self._progress_value = value

    def _run_task(self) -> None:
        try:
            result = self.task(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self._error = (exctype, value, traceback.format_exc())
        else:
            self._result = result
        finally:
            self._done.set()

    async def _monitor_loop(self) -> None:
        last_progress: Tuple[Optional[str], Optional[int]] = (None, None)

        while not self._done.is_set():
            await asyncio.sleep(0.1)
            with self._progress_lock:
                if (self._progress_message, self._progress_value) != last_progress:
                    last_progress = (self._progress_message, self._progress_value)
                    await self._call_callback(self._on_progress, *last_progress)

        # After done
        if self._error:
            await self._call_callback(self._on_error, *self._error)
        else:
            await self._call_callback(self._on_result, self._result)

        await self._call_callback(self._on_finished)

    async def _call_callback(self, callback: Optional[Callable], *args: Any) -> None:
        if callback is None:
            return
        try:
            if inspect.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception:
            traceback.print_exc()

    @override
    def connect_error(self, callback: Callable[[Any], None]) -> None:
        self._on_error = callback

    @override
    def connect_result(self, callback: Callable[[Any], None]) -> None:
        self._on_result = callback

    @override
    def connect_finished(self, callback: Callable[[], None]) -> None:
        self._on_finished = callback

    @override
    def connect_progress(self, callback: Callable[[str, int], None]) -> None:
        self._on_progress = callback

    @override
    def start(self) -> None:
        self._thread.start()
        if is_async():
            asyncio.create_task(self._monitor_loop())
        else:
            raise Exception("Trame Worker should run from an async loop")
