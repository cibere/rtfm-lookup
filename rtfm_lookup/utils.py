from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _collections_abc import dict_keys, dict_values
    from collections.abc import Iterator

    from yarl import URL

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

    def __iter__(self) -> Iterator[Manual]:
        return self.__actual.values().__iter__()


def remove_page_path(url: URL):
    if not url.parts[-1].endswith(".html"):
        return url

    parts = list(url.parts[0:-1])
    while "/" in parts:
        parts.remove("/")
    return url.with_path("").joinpath(*parts)
