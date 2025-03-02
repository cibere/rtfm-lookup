from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

import msgspec
from aiohttp import ClientSession
from cidex.v2_1 import ApiIndex, ApiRequest, Cache, CacheIndex, VariantManifest
from yarl import URL

from ..enums import IndexerName
from .base import Indexer

if TYPE_CHECKING:
    from collections.abc import Iterable

    from aiohttp import ClientSession


CidexResponse = CacheIndex | VariantManifest | ApiIndex
msgpack = msgspec.msgpack.Decoder(type=CidexResponse)
api_decoder = msgspec.json.Decoder(type=CacheIndex)
json_encoder = msgspec.json.Encoder()
INDEX_URL = "https://github.com/cibere/Rtfm-Indexes/raw/refs/heads/indexes-v2/indexes_v2/{}.cidex"


class _CidexIndexerBase(Indexer, name=IndexerName.cidex):
    _api_info: ApiIndex

    @abstractmethod
    def _get_url(self) -> URL:
        raise NotImplementedError

    def _resolve_variant_via_exact_match(
        self, url: URL, variants: Iterable[str]
    ) -> str | None:
        choice = None

        for variant in variants:
            if variant in url.path:
                if choice is not None:
                    return
                choice = variant
        return choice

    def resolve_variant(self, manifest: VariantManifest) -> str | None:
        # This "proxy" method is used for future-proofing, so that its "easier" to add more matching methods
        return self._resolve_variant_via_exact_match(self.loc, manifest.variants)

    async def fetch_index(
        self, session: ClientSession, url: URL
    ) -> CacheIndex | ApiIndex:
        if self.manual.options.get("file_override"):
            raw_content = self.manual["file_override"].read_bytes()
        else:
            async with session.get(url) as res:
                raw_content: bytes = await res.content.read()

        data: CidexResponse = msgpack.decode(raw_content)

        if isinstance(data, VariantManifest):
            variant = self.resolve_variant(data)
            if not variant:
                raise ValueError("Unable to resolve correct variant")

            parts = list(url.parts)
            parts[-1] = parts[-1].replace(".cidex", f"-{variant}.cidex")
            new_url = url.with_path("/".join(parts))

            assert new_url != url
            return await self.fetch_index(session, new_url)

        return data

    async def build_cache(self) -> Cache:
        url = self._get_url()
        index = await self.fetch_index(self.session, url)

        if isinstance(index, ApiIndex):
            self._api_info = index
            self.make_request = self._make_request
            cache = {}
        else:
            cache = index.cache

        self.favicon_url = index.favicon_url
        return cache

    async def _make_request(self, query: str) -> Cache:
        info = self._api_info

        payload = ApiRequest(query=query, options=info.options)
        async with self.session.post(
            info.url, data=json_encoder.encode(payload)
        ) as res:
            raw_content = await res.read()

        return api_decoder.decode(raw_content).cache


class CibereRtfmIndex(_CidexIndexerBase, name=IndexerName.cibere_rtfm_indexes):
    def _get_url(self) -> URL:
        index_url = INDEX_URL.format(str(self.loc.host).removeprefix("www."))
        return URL(index_url)


class Cidex(_CidexIndexerBase, name=IndexerName.cidex):
    def _get_url(self) -> URL:
        return self.loc.with_path("index.cidex")
