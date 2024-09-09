import functools
from abc import ABC, abstractmethod


class BindingInterface(ABC):
    @abstractmethod
    def new_bind(self, linked_object=None, linked_object_arguments=None, callback_after_update=None):
        raise Exception("Please implement in a concrete class")


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split('.'))
