from __future__ import annotations

from typing import Any

import msgspec

__all__ = ("Entry",)


class Entry(msgspec.Struct):
    text: str
    url: str
    options: dict[str, Any] = msgspec.field(default_factory=dict)
