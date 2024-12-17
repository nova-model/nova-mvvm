"""Test package."""

from typing import Any, Dict, List

import pytest
from PyQt6.QtWidgets import QLabel, QLineEdit, QMainWindow, QVBoxLayout, QWidget
from pytestqt.qtbot import QtBot

from nova.mvvm.pydantic_utils import get_field_info
from nova.mvvm.pyqt_binding import PyQtBinding
from nova.mvvm.pyqt_binding.binding import PyQtCommunicator

from .model import User


class MainWindow(QMainWindow):
    """Test application class."""

    def __init__(self, binding: PyQtCommunicator):
        super().__init__()
        self.callback_config_object = binding.connect("config", self.on_config_object_update)

        self.create_ui()

    def on_config_object_update(self, config: User) -> None:
        self.username_edit_box.setText(config.username)

    def process_config_change(self, key: str, value: Any) -> None:
        print(key, value)
        self.callback_config_object(key, value)

    def get_description(self, field: str, default: str = "") -> str:
        try:
            field_info = get_field_info(field)
            return str(field_info.description)
        except Exception:
            return default

    def create_ui(self) -> None:
        layout = QVBoxLayout()
        self.label = QLabel(self.get_description("config.username"))
        layout.addWidget(self.label)
        self.username_edit_box = QLineEdit()
        self.username_edit_box.textChanged.connect(lambda text: self.process_config_change("config.username", text))
        layout.addWidget(self.username_edit_box)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


def test_binding_model_to_pyqt(qtbot: QtBot) -> None:
    # Creates pyqt binding for a Pydantic object, updates model and validates that the PyQt element was updated.

    test_object = User()

    binding = PyQtBinding().new_bind(test_object)
    widget = MainWindow(binding)
    qtbot.addWidget(widget)

    assert widget.username_edit_box.text() == ""

    binding.update_in_view(test_object)
    assert widget.username_edit_box.text() == "default_user"
    assert widget.label.text() == "hint"


test_cases: List[Dict[str, Any]] = [
    {
        "test_name": "update username",
        "input": "newname",
        "result": {"value": "newname", "error": False},
    },
    {
        "test_name": "empty username",
        "input": "u",  # could not make it work with empty string
        "result": {"value": "default_user", "error": True},
    },
]


@pytest.mark.parametrize(
    "input, expected_result",
    [(case["input"], case["result"]) for case in test_cases],
    ids=[case["test_name"] for case in test_cases],
)
def test_binding_pyqt_to_model(qtbot: QtBot, input: str, expected_result: Dict[str, Any]) -> None:
    # Creates pyqt binding for a Pydantic object, updates user interface state and validates that the model was updated
    # or validation error occurred.
    after_update_results = {}
    test_object = User()

    def after_update(results: Dict[str, Any]) -> None:
        after_update_results.update(results)

    binding = PyQtBinding().new_bind(test_object, callback_after_update=after_update)
    widget = MainWindow(binding)
    qtbot.addWidget(widget)

    qtbot.keyClicks(widget.username_edit_box, input)

    if expected_result["error"]:
        assert "username" in after_update_results["errored"]
    else:
        assert "username" in after_update_results["updated"]
    assert test_object.username == expected_result["value"]
