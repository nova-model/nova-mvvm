Data Binding: The Heart of MVVM
-------------------------------

*Data binding* is a mechanism that allows the View and the ViewModel to
automatically synchronize their data. When the data in the ViewModel
changes, the View is automatically updated to reflect the changes.
Conversely, when the user interacts with the View (e.g., by entering
text in a field), the data in the ViewModel is automatically updated.

This data binding is what makes MVVM so powerful and allows for reactive
UIs. Instead of manually writing code to update the UI every time the
data changes, you simply bind the UI components to the data in the
ViewModel, and the updates happen automatically.


Data Binding with NOVA
----------------------

The **nova-mvvm** library greatly simplifies the data
synchronization between the components of an MVVM application and
provides support for user interfaces utilizing the Trame, PyQt, and
Panel graphical frameworks. The library provides several predefined
classes including TrameBinding, PyQtBinding, and PanelBinding to connect
UI components to model variables.

Here, we will focus on the TrameBinding class, but all three function similarly.

How to use TrameBinding
~~~~~~~~~~~~~~~~~~~~~~~

The initial step is to create a BindingInterface. A BindingInterface
serves as the foundational layer for how connections are made between
variables in the ViewModel and UI components in the View. Once a Trame
application has started, the :class:`nova.mvvm.interface.BindingInterface` can be created in the View
with:

.. code:: python

   bindingInterface = TrameBinding(self.server.state) # server is the Trame Server

After a BindingInterface has been created, variables must be added to
the interface via the interface's ``new_bind`` method. The ``new_bind``
method expects a variable that will be linked to a UI component, and an
optional callback method. The callback method is useful if there are
actions to be performed after updates to the UI. In the code snippet
below, we’ve passed the Binding Interface to the ViewModel. The
ViewModel adds the ``model`` variable to the binding interface. This
``new_bind`` method returns a :class:`nova.mvvm.interface.Communicator`. The ``Communicator`` is
an object which manages the binding and will be used to propgate
updates.

.. code:: python

   # Adding a binding to the Binding Interface, returns a Communicator
   self.config_bind = bindingInterface.new_bind(self.model)

The ``self.config_bind`` object is a ``Communicator`` and is used to
update the View. When the ViewModel needs to tell the View to perform an
Update, it calls the ``update_in_view`` method of the ``Communicator``.
For the ``self.config_bind`` object, the ViewModel would make a call
like below. It is common practice for the ViewModel to have a method
such as update_view, where ViewModel would update many objects. However,
there are also times when it is appropriate to only update a singular
object.

.. code:: python

   # Updating the UI connected to a binding.
   def update_view(self) -> None:
       self.config_bind.update_in_view(self.model)

We've seen how to create a BindingInterface, add a new binding, and how
to perform updates. We also need to connect our View components to the
Communicators. The Communicator class has a ``connect`` method. This
method accepts a callable object or a string. If you pass a callable
object, such as a method, that object will be called whenever the
binding's update_in_view method is called. In the example below, we
connect to the ``config_bind`` Communicator object that was created in
our ViewModel. When a string is passed to the connect method, that
string will be used as the unique name of our connector. In this
example, we pass in the string ``config`` but you are free to use any
string that is not already in use as a connector.

.. code:: python

   self.view_model.config_bind.connect("config")
