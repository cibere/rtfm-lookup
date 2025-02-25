from enum import Enum

__all__ = ("IndexerName",)


class IndexerName(Enum):
    mkdocs = "mkdocs"
    intersphinx = "intersphinx"
    gidocgen = "gidocgen"
    cidex = "cidex"
    cibere_rtfm_indexes = "cibere-rtfm-indexes"
