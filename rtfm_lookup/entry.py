from __future__ import annotations

from typing import Any

__all__ = ("Entry",)


class Entry:
    def __init__(
        self,
        text: str,
        url: Any,
        options: dict[str, Any] | None = None,
    ) -> None:
        self.text = text
        self.url = str(url)
        self.options = options or {}
