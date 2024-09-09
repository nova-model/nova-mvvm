try:
    from PyQt6.QtCore import pyqtSignal, QObject
except:
    print("PyQt6 is missing. You could install 'py-mvvm[pyqt6]' to fix it")
    exit(1)

import inspect

from ..interface import BindingInterface, rsetattr


def is_callable(var):
    return inspect.isfunction(var) or inspect.ismethod(var)


class Communicate(QObject):
    signal = pyqtSignal(object)

    def __init__(self, viewmodel_linked_object=None, linked_object_attributes=None, callback_after_update=None):
        super().__init__()
        self.viewmodel_linked_object = viewmodel_linked_object
        self.linked_object_attributes = linked_object_attributes
        self.callback_after_update = callback_after_update

    def _update_viewmodel_callback(self, key=None, value=None):
        if isinstance(self.viewmodel_linked_object, dict):
            self.viewmodel_linked_object.update({key: value})
        elif is_callable(self.viewmodel_linked_object):
            self.viewmodel_linked_object(value)
        elif isinstance(self.viewmodel_linked_object, object):
            rsetattr(self.viewmodel_linked_object, key, value)
        else:
            raise Exception("Cannot update", self.viewmodel_linked_object)

        if self.callback_after_update:
            self.callback_after_update(key)

    def connect(self, *args, **kwargs):
        # connect should be called from the View side to connect a
        # GUI element (via a function to change GUI element that is passed to the connect call)
        # and a linked_object (passed during bind creation from ViewModel side)
        self.signal.connect(*args, **kwargs)
        if self.viewmodel_linked_object:
            return self._update_viewmodel_callback
        else:
            return None

    def update_in_view(self, *args, **kwargs):
        # this updates a View (GUI) when called by a ViewModel
        return self.signal.emit(*args, **kwargs)


class PyQtBinding(BindingInterface):
    def new_bind(self, linked_object=None, linked_object_arguments=None, callback_after_update=None):
        # each new_bind returns an object that can be used to bind a ViewModel/Model variable
        # with a corresponding GUI framework element
        # for PyQt we use pyqtSignal to trigger GUI update and linked_object to trigger ViewModel/Model update
        return Communicate(linked_object, linked_object_arguments, callback_after_update)
