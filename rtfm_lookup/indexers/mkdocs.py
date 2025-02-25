from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from ..entry import Entry
from ..enums import IndexerName
from .base import Indexer

if TYPE_CHECKING:
    from .._types import Cache


class DocEntry(msgspec.Struct):
    location: str
    text: str
    title: str


class SearchIndexFile(msgspec.Struct):
    config: dict
    docs: list[DocEntry]


search_file_decoder = msgspec.json.Decoder(type=SearchIndexFile)


class Mkdocs(Indexer, name=IndexerName.mkdocs):
    async def build_cache(self) -> Cache:
        async with self.session.get(self / "search" / "search_index.json") as res:
            raw_content: bytes = await res.content.read()

        data = search_file_decoder.decode(raw_content)

        return {
            entry.title: Entry(entry.title, self / entry.location)
            for entry in data.docs
        }
