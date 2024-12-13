"""Module for storing and accessing MVVM bindings.

This module contains a global dictionary, `bindings_map`, which holds the MVVM (Model-View-ViewModel) bindings.
Each binding is stored with a name as the key, allowing easy lookup and access to the associated binding from GUI
by using a field name (first part of which would be the binding key).
"""

from typing import Any, Dict

bindings_map: Dict[str, Any] = {}
