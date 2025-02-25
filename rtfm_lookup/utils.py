from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _collections_abc import dict_keys, dict_values

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

    def keys(self) -> dict_keys[str, Manual]:
        return self.__actual.keys()

    names = keys

    def values(self) -> dict_values[str, Manual]:
        return self.__actual.values()

    def clear(self) -> None:
        self.__actual.clear()
