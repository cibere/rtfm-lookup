from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import msgspec

from .enums import IndexerName  # noqa: TC001 # for msgspec to resolve

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from yarl import URL

    from ._types import Cache
    from .entry import Entry
    from .indexers import Indexer
    from .manager import RtfmManager


class PartialManual(msgspec.Struct):
    name: str
    type: IndexerName
    loc: str
    options: dict[str, Any] = msgspec.field(default_factory=dict)


class Manual:
    cache: Cache | None

    def __init__(
        self,
        name: str,
        loc: URL,
        *,
        indexer: type[Indexer],
        manager: RtfmManager,
        options: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.loc = loc
        self.manager = manager
        self.indexer = indexer(self)
        self.options = self.manager.options["default_manual_options"].copy() or {}

        self.cache = None
        if options:
            self.options.update(options)

    @property
    def is_api(self) -> bool:
        return self.options.get("is_api", False)

    @property
    def favicon_url(self) -> str | None:
        return self.indexer.favicon_url

    def __init_subclass__(cls, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(cls, key, value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name=} {self.loc=} {self.is_api=}>"

    def __getitem__(self, key: str) -> Any:
        return self.options.__getitem__(key)

    def __setitem__(self, key: str, value: Any) -> None:
        return self.options.__setitem__(key, value)

    def to_partial(self) -> PartialManual:
        return PartialManual(
            self.name, type=self.indexer.name, loc=str(self.loc), options=self.options
        )

    async def refresh_cache(self) -> Cache:
        self.cache = await self.indexer.build_cache()
        return self.cache

    async def query(self, text: str) -> AsyncIterator[tuple[int, Entry]]:
        if self.cache is None:
            self.cache = await self.refresh_cache()

        await self.indexer.pre_query_hook(text)
        matches = await asyncio.to_thread(self.manager.fuzzy_search, text, self.cache)

        for idx, (_, match) in enumerate(matches):
            yield idx, match
