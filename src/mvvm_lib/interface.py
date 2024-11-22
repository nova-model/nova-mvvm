"""Abstract interfaces and type definitions."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Union

LinkedObjectType = Optional[Any]
LinkedObjectAttributesType = Optional[list[str]]
CallbackAfterUpdateType = Optional[Callable[[Optional[str]], None]]
ConnectCallbackType = Union[None, Callable[[Any, Optional[str]], None]]


class Communicator(ABC):
    """Abstract communicator class.

    Provides methods required for binding to communicate between ViewModel and View.
    """

    @abstractmethod
    def connect(self, connector: Any = None) -> ConnectCallbackType:
        """
        Connect a GUI element to a linked object.

        This method should be called from the View side to establish a
        connection between a GUI element and a linked object, which
        is passed during the bind creation from the ViewModel side.

        Parameters
        ----------
        connector : Any, optional
            The GUI element or object to connect. None can be used in some implementations
            to indicate that GUI element(s) should be automatically identified using the linked object.

        Returns
        -------
        Union[None, Callable]
        Depending on the specific implementation, returns None or a callback function
        that can be used to update the linked object.
        """
        raise Exception("Please implement in a concrete class")

    @abstractmethod
    def update_in_view(self, value: Any) -> None:
        """
        Update UI component(s) with the provided value.

        Parameters
        ----------
        value : Any
            The new value to be reflected in the view.

        Returns
        -------
        None
            This method does not return a value.
        """
        raise Exception("Please implement in a concrete class")


class BindingInterface(ABC):
    """Abstract binding interface."""

    @abstractmethod
    def new_bind(
        self,
        linked_object: LinkedObjectType = None,
        linked_object_arguments: LinkedObjectAttributesType = None,
        callback_after_update: CallbackAfterUpdateType = None,
    ) -> Communicator:
        """
        Bind a ViewModel or Model variable to a GUI framework element, allowing for synchronized updates.

        This method creates a binding between a variable in a ViewModel/Model and a corresponding element
        in the GUI.

        Parameters
        ----------
        linked_object : object, dictionary or function, optional
            Instance to link with the ViewModel/Model variable. When specified, changes in View
            trigger update for this instance.

        linked_object_arguments : list of str, optional
            If the `linked_object` is a class instance(object) one can provide a list of argument names associated
            with `linked_object` that define specific attributes
            to bind. If not provided, the default behavior is to bind all attributes.

        callback_after_update : Callable, optional
            A function to be called after each update to `linked_object`. Useful for additional
            actions or processing post-update.

        Returns
        -------
        Communicator
            An object that manages the binding, allowing updates to propagate between the
            ViewModel/Model variable and the GUI framework element.
        """
        raise Exception("Please implement in a concrete class")
