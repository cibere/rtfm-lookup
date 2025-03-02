from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiohttp import ClientSession
    from cidex.v2_1 import Cache
    from yarl import URL

    from ..enums import IndexerName
    from ..manual import Manual


__all__ = ("Indexer",)


class Indexer(ABC):
    name: ClassVar[IndexerName]
    make_request: Callable[[str], Awaitable[Cache]] | None = None

    def __init__(self, manual: Manual) -> None:
        self.manual = manual
        self.favicon_url: str | None = None

    def __init_subclass__(cls, name: IndexerName, **kwargs: Any) -> None:
        kwargs["name"] = name

        for key, value in kwargs.items():
            setattr(cls, key, value)

    @property
    def loc(self) -> URL:
        return self.manual.loc

    @property
    def session(self) -> ClientSession:
        return self.manual.manager._session

    def __truediv__(self, other: str) -> URL:
        return self.loc.__truediv__(other)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.manual=} {self.favicon_url=}>"

    @abstractmethod
    async def build_cache(self) -> Cache:
        raise NotImplementedError
