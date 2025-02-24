from enum import Enum

__all__ = ("IndexerName",)


class IndexerName(Enum):
    mdocs = "mdocs"
    intersphinx = "intersphinx"
    gidocgen = "gidocgen"
    cidex = "cidex"
    cibere_rtfm_indexes = "cibere-rtfm-indexes"
