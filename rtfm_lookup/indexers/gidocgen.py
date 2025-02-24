from __future__ import annotations

import msgspec

from ..entry import Entry
from ..enums import IndexerName
from .base import Indexer

TYPE_CHECKING = False
if TYPE_CHECKING:
    from .._types import (
        Cache,  # noqa: TC001 # this will be fixed in the next ruff release
    )


TYPE_REPLACEMENTS = {
    "record": "struct",
    "constant": "const",
    "domain": "error",
    "bitfield": "flags",
    "function_macro": "func",
    "function": "func",
    "interface": "iface",
}


class DocEntry(msgspec.Struct):
    name: str
    summary: str
    ident: str | None = None
    ctype: str | None = None
    type_name: str | None = None
    type: str | None = None
    href: str | None = None
    deprecated: str | None = None
    struct_for: str | None = None

    @property
    def type_or_struct(self):
        return self.struct_for or self.type_name

    def build_label(self):
        parts = []
        if self.type and (entry_type := TYPE_REPLACEMENTS.get(self.type, self.type)):
            parts.append(entry_type)
        if self.type_or_struct:
            parts.append(self.type_or_struct)
        parts.append(self.name)

        return ".".join(parts)


class GiDocGenIndex(msgspec.Struct):
    symbols: list[DocEntry]


index_decoder = msgspec.json.Decoder(type=GiDocGenIndex)


class GidocgenDocType(Indexer, name=IndexerName.gidocgen):
    async def build_cache(self) -> Cache:
        async with self.session.get(self / "index.json") as res:
            raw_content: bytes = await res.content.read()

        data = index_decoder.decode(raw_content)
        cache: Cache = {}

        for entry in data.symbols:
            label = entry.build_label()
            href = entry.href or f"{label}.html"
            url = self / href

            cache[label] = Entry(label, str(url))

        return cache
