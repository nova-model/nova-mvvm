"""Test package."""

import asyncio
from typing import Any, Dict

import pytest
from pydantic import BaseModel, Field
from trame.app import get_server

from nova.mvvm.trame_binding import TrameBinding


class User(BaseModel):
    """User model for tests."""

    username: str = Field(default="test_name", min_length=1, title="User Name", description="hint", examples=["user"])


@pytest.mark.asyncio
async def test_pydantic() -> None:
    res = {}

    async def after_update(results: Dict[str, Any]) -> None:
        res.update(results)

    server = get_server()

    obj = User()
    binding = TrameBinding(server.state).new_bind(obj, callback_after_update=after_update)
    binding.connect("obj")
    binding.update_in_view(obj)

    asyncio.create_task(server.start(exec_mode="coroutine", open_browser=False))
    await asyncio.sleep(1)
    server.state["obj"]["username"] = "aa"
    with server.state:
        server.state.dirty("obj")
        server.state.flush()
    await server.stop()
    print(res)
    assert "username" in res["updated"]
