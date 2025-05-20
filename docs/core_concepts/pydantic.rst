Introduction to Pydantic
------------------------

`Pydantic <https://docs.pydantic.dev/latest/>`_ is a Python library that provides a powerful and elegant way to
define data models and enforce data validation. It uses Python type
hints to define the structure of your data and automatically validates
data against these types at runtime.

Key Features of Pydantic:

-  **Data Validation:** Automatically validates data types and
   constraints, ensuring data integrity. Pydantic supports a wide range
   of validation options, including type checking, length constraints,
   regular expressions, custom validators, and more.
-  **Clear Data Structures:** Defines data models in a clear and
   readable way using Python type hints. Pydantic models are easy to
   understand and maintain.
-  **Serialization and Deserialization:** Easily serializes data to and
   from standard formats like JSON. This is useful for interacting with
   APIs and other external systems.
-  **Settings Management:** Can be used to manage application settings
   and configuration, providing a centralized and type-safe way to
   access configuration values.
-  **Improved Code Readability:** Makes code easier to understand and
   maintain by explicitly defining data models. Type hints make it clear
   what type of data is expected for each field.

How Pydantic Works
------------------

Pydantic uses Python type hints to define data models. When you create
an instance of a Pydantic model, Pydantic automatically validates the
input data against the defined types and constraints.

For edxample, let's define a ``User`` model with two fields: ``id`` and
``name``. We use type hints to specify the data type for each field
(e.g., ``int``, ``str``) and ``Field`` with validation arguments to
specify additional constraints (e.g., ``gt=0``, ``min_length=1``, …).

.. code:: python

   from pydantic import BaseModel, Field

   class User(BaseModel):
       id: int = Field(default=1, gt=0)  # id must be an integer greater than 0
       name: str = Field(default="someName", min_length=1) # name must be a string with at least one character


When you create an instance of the ``User`` model, Pydantic
automatically validates the input data.

If the input data is invalid, Pydantic raises a ``ValidationError``
exception with detailed information about the validation errors.


Using Pydantic models in NOVA-MVVM
---------------------------------------

NOVA-MVVM allows an application to leverage Pydantic models to automatically validate UI
elements. All you need to do is to create a binding for a model and connect it to a GUI element.
On GUI update, the model will be validated and any errors reported in the callback function.
