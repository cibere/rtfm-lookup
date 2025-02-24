from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .manual import Manual

__all__ = ("ManualsIterable",)


class ManualsIterable:
    def __init__(self, actual: dict[str, Manual]) -> None:
        self.__actual = actual

    def add(self, manual: Manual) -> None:
        self.__actual[manual.name] = manual

    append = add

    def remove(self, manual: Manual) -> None:
        self.__actual.pop(manual.name, None)

    def __len__(self) -> int:
        return self.__actual.__len__()

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, str):
            return item in self.__actual
        return item in self.__actual.values()
