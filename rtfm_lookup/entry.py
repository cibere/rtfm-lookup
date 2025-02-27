from __future__ import annotations

from typing import Any, Self

import msgspec

__all__ = ("Entry",)


class Entry(msgspec.Struct):
    text: str
    url: str
    options: dict[str, Any] = msgspec.field(default_factory=dict)

    def copy(self) -> Self:
        return Entry(text=self.text, url=self.url, options=self.options)  # pyright: ignore[reportReturnType]
