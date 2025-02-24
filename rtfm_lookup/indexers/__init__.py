from __future__ import annotations

from .base import Indexer as Indexer  # noqa: TC001
from .cidex import CibereRtfmIndex, Cidex
from .gidocgen import GidocgenDocType
from .intersphinx import InterSphinx
from .mkdocs import Mkdocs

TYPE_CHECKING = False
if TYPE_CHECKING:
    from ..enums import (
        IndexerName,  # noqa: TC001 # this will be fixed in the next ruff release
    )


indexers: dict[IndexerName, type[Indexer]] = {
    indexer.name: indexer
    for indexer in (
        Cidex,
        CibereRtfmIndex,
        GidocgenDocType,
        InterSphinx,
        Mkdocs,
    )
}
