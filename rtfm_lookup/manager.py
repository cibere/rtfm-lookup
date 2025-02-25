from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Literal, Self

import aiohttp
import msgspec
from yarl import URL

from .better_lock import BetterLock
from .filler import Filler
from .fuzzy import finder as _fuzzy_finder
from .indexers import indexers
from .manual import Manual, PartialManual
from .utils import ManualsIterable

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
    from types import TracebackType

    from ._types import Cache
    from .entry import Entry
    from .enums import IndexerName

__all__ = ("RtfmManager",)

log = logging.getLogger(__name__)


class RtfmManager:
    _session: aiohttp.ClientSession

    def __init__(self) -> None:
        self.cache_lock = BetterLock()
        self._manuals: dict[str, Manual] = {}
        self._session = Filler(
            "Rtfm Manager has not been initialized yet. You can do so by using it as a context manager, or awaiting the manager."
        )  # pyright: ignore[reportAttributeAccessIssue]

    @property
    def manuals(self) -> ManualsIterable:
        return ManualsIterable(self._manuals)

    def __await__(self) -> Generator[Any, Any, Self]:
        return self.__aenter__().__await__()

    async def close(self):
        await self._session.close()

    async def __aenter__(self) -> Self:
        self._session = await aiohttp.ClientSession().__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> bool | None:
        return await self.close()

    def __setitem__(self, key: str, value: Manual) -> None:
        self._manuals[key] = value
        value.name = key

    def __getitem__(self, key: str) -> Manual:
        return self._manuals.__getitem__(key)

    def fuzzy_search(self, text: str, cache: Cache) -> Iterator[tuple[str, Entry]]:
        return reversed(_fuzzy_finder(text, list(cache.items()), key=lambda t: t[0]))

    async def reload_cache(self) -> None:
        if self.cache_lock.locked():
            return await self.cache_lock.wait()

        async with self.cache_lock:
            await asyncio.gather(
                *(man.refresh_cache() for man in self._manuals.values())
            )

    async def get_manual(
        self,
        name: str,
        url: str | URL,
        *,
        add: bool = True,
        indexer_name: IndexerName | None = None,
    ) -> Manual | None:
        if isinstance(url, str):
            url = URL(url.rstrip("/"))

        for indexer in indexers.values():
            if indexer_name and indexer.name is not indexer_name:
                continue

            man = Manual(name, url, indexer=indexer, manager=self)
            try:
                await man.refresh_cache()
            except Exception as e:
                log.debug("Wrong indexer for %r: %r", url, man.indexer.name, exc_info=e)

                if getattr(e, "__rtfm_lookup_force_raise__", False):
                    raise e
                del man
            else:
                if add:
                    self[man.name] = man  # noqa: F821 # false positive: https://github.com/astral-sh/ruff/issues/16358

                return man  # noqa: F821 # false positive: https://github.com/astral-sh/ruff/issues/16358

    def export(self, format: Literal["json", "yaml", "msgpack"] = "json") -> bytes:
        match format:
            case "json":
                encoder = msgspec.json.encode
            case "yaml":
                encoder = msgspec.yaml.encode
            case "msgpack":
                encoder = msgspec.msgpack.encode

        def enc_hook(obj: Any) -> Any:
            if isinstance(obj, Manual):
                return obj.to_partial()
            return repr(obj)

        return encoder(list(self._manuals.values()), enc_hook=enc_hook)

    def import_(
        self, data: bytes, format: Literal["json", "yaml", "msgpack"] = "json"
    ) -> None:
        match format:
            case "json":
                decoder = msgspec.json.decode
            case "yaml":
                decoder = msgspec.yaml.decode
            case "msgpack":
                decoder = msgspec.msgpack.decode

        partial_manuals = decoder(data, type=list[PartialManual])

        for partial_manual in partial_manuals:
            man = Manual(
                partial_manual.name,
                URL(partial_manual.loc),
                indexer=indexers[partial_manual.type],
                manager=self,
                options=partial_manual.options,
            )
            self[man.name] = man

    def load_partial(self, partial: PartialManual, *, add: bool = True) -> Manual:
        man = Manual(
            partial.name,
            URL(partial.loc),
            indexer=indexers[partial.type],
            manager=self,
            options=partial.options,
        )

        if add:
            self[man.name] = man
        return man

    def load_partials(self, *partials: PartialManual) -> None:
        for partial in partials:
            self.load_partial(partial)