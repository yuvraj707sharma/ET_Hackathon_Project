from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CatalogItem:
    id: str
    title: str
    productType: str
    categoryTags: list[str]
    audienceHint: str
    url: str
    lastUpdatedISO: str | None = None

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "CatalogItem":
        return CatalogItem(
            id=d["id"],
            title=d["title"],
            productType=d["productType"],
            categoryTags=list(d.get("categoryTags", [])),
            audienceHint=d.get("audienceHint", ""),
            url=d["url"],
            lastUpdatedISO=d.get("lastUpdatedISO"),
        )


def load_product_catalog(catalog_path: str | Path) -> list[CatalogItem]:
    path = Path(catalog_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [CatalogItem.from_dict(x) for x in raw]


def build_basic_search_index(items: list[CatalogItem]) -> dict[str, list[CatalogItem]]:
    """
    Simple tag->items lookup. We avoid live scraping so the demo works reliably.
    """
    index: dict[str, list[CatalogItem]] = {}
    for item in items:
        for tag in item.categoryTags:
            index.setdefault(tag, []).append(item)
    return index

