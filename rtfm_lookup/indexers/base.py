from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from aiohttp import ClientSession
    from yarl import URL

    from .._types import Cache
    from ..enums import IndexerName
    from ..manual import Manual


__all__ = ("Indexer",)


class Indexer(ABC):
    name: ClassVar[IndexerName]

    def __init__(self, manual: Manual) -> None:
        self.manual = manual
        self.favicon_url: str | None = None
        self.is_api = False

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
        return f"<{self.__class__.__name__}>"

    async def pre_query_hook(self, query: str) -> None:
        pass

    @abstractmethod
    async def build_cache(self) -> Cache:
        raise NotImplementedError
