"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

# help with: http://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/

from __future__ import annotations

import re
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    TypeVar,Iterator
)

if TYPE_CHECKING:
    from collections.abc import Iterable

T = TypeVar("T")

def finder(
    text: str,
    collection: Iterable[T],
    *,
    key: Callable[[T], str] | None = None,
) -> Iterator[T]:
    suggestions: list[tuple[int, int, T]] = []
    text = str(text)
    pat = ".*?".join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else str(item)
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup: tuple[int, int, T]) -> tuple[int, int, str | T]:
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    for _, _, item in reversed(sorted(suggestions, key=sort_key)):
        yield item
