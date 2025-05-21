MVVM Example Using Trame Framework
==================================

This example demonstrates a simple application using the MVVM (Model-View-ViewModel) design pattern.
We'll use the `Trame` framework along with the `TrameBinding` interface from `nova-mvvm`.

For more information and examples, we recommend looking at the tutorial from the
`Neutrons Open Visualization and Analysis (NOVA) Framework Developer Workshop <https://example.com/nova-tutorial>`_.


MVVM consists of three parts:

- **Model**: Represents the data and business logic.
- **View**: Represents the UI.
- **ViewModel**: Acts as a bridge between the Model and the View.

Model
-----

Create a `model.py` file to define the main model.

.. code-block:: python
    :caption: model.py

    """Module for the main model."""

    from pydantic import BaseModel, Field

    class MainModel(BaseModel):
        """
        A model class.

        This class uses Pydantic (https://docs.pydantic.dev/latest/) for
        data validation, metadata, and examples that can improve UI generation.
        """

        username: str = Field(
            default="test_name",
            min_length=1,
            title="User Name",
            description="Please provide the name of the user",
            examples=["user"],
        )
        password: str = Field(default="test_password", title="User Password")


ViewModel
---------

Create a `view_model.py` file to define the ViewModel logic.

.. code-block:: python
    :caption: view_model.py

    """Module for the main ViewModel."""

    from typing import Any, Dict
    from nova.mvvm.interface import BindingInterface
    from ..models.main_model import MainModel

    class MainViewModel:
        """ViewModel class: manages data-view bindings and reacts to UI changes."""

        def __init__(self, model: MainModel, binding: BindingInterface):
            self.model = model

            # Create a bind between the ViewModel and the View
            self.config_bind = binding.new_bind(
                self.model,
                callback_after_update=self.change_callback
            )

        def change_callback(self, results: Dict[str, Any]) -> None:
            if results["error"]:
                print(f"Error in fields {results['errored']}, model not changed")
            else:
                print(f"Model fields updated: {results['updated']}")

        def update_view(self) -> None:
            self.config_bind.update_in_view(self.model)


View
----

Create a `view.py` file to define the UI.

.. code-block:: python
    :caption: view.py

    """Main view file."""

    import logging
    from nova.mvvm.trame_binding import TrameBinding
    from nova.trame import ThemedApp
    from trame.app import get_server
    from nova.trame.view.components import InputField
    from trame.widgets import vuetify3 as vuetify

    from ..view_models.main import MainViewModel
    from ..models.main_model import MainModel

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    class MainApp(ThemedApp):
        """Main application view class. Renders UI elements."""

        def __init__(self) -> None:
            super().__init__()
            self.server = get_server(None, client_type="vue3")
            binding = TrameBinding(self.server.state)
            self.server.state.trame__title = "Test Project"

            model = MainModel()
            self.view_model = MainViewModel(model, binding)
            self.view_model.config_bind.connect("config")
            self.create_ui()

        def create_ui(self) -> None:
            self.state.trame__title = "Test Project"

            with super().create_ui() as layout:
                layout.toolbar_title.set_text("Test Project")

                with layout.pre_content:
                    pass

                with layout.content:
                    with vuetify.VRow(align="center", classes="mt-4"):
                        InputField("config.username")
                    with vuetify.VRow(align="center"):
                        InputField("config.password")

                with layout.post_content:
                    pass

                return layout


Application Entry Point
-----------------------

Create a `main.py` file to start the application.

.. code-block:: python
    :caption: main.py

    """Main Application."""

    def main() -> None:
        from .views.main import MainApp
        app = MainApp()
        app.server.start()
