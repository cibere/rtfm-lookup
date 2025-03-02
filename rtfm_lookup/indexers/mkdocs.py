from __future__ import annotations

import msgspec
from cidex.v2_1 import Entry, MutableCache

from ..enums import IndexerName
from .base import Indexer


class DocEntry(msgspec.Struct):
    location: str
    text: str
    title: str


class SearchIndexFile(msgspec.Struct):
    config: dict
    docs: list[DocEntry]


search_file_decoder = msgspec.json.Decoder(type=SearchIndexFile)


class Mkdocs(Indexer, name=IndexerName.mkdocs):
    async def build_cache(self) -> MutableCache:
        async with self.session.get(self / "search" / "search_index.json") as res:
            raw_content: bytes = await res.content.read()

        data = search_file_decoder.decode(raw_content)

        return {
            entry.title: Entry(entry.title, str(self / entry.location))
            for entry in data.docs
        }
