from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Generic, TypeVar


T = TypeVar("T")


class FixtureRepository(Generic[T]):
    def __init__(
        self,
        files: Iterable[Path],
        *,
        key_builder: Callable[[Path], tuple[str, ...]],
        loader: Callable[[Path], T],
        separator: str = ".",
    ) -> None:
        self._separator = separator
        self._items = {
            tuple(
                part.lower()
                for part in key_builder(file)
            ): loader(file)
            for file in files
        }

    def get(
        self,
        *key: str,
    ) -> T:
        return self._items[
            tuple(part.lower() for part in key)
        ]

    def get_qualified(
        self,
        key: str,
    ) -> T:
        return self.get(
            *key.lower().split(self._separator)
        )

    def query(
        self,
        *parts: str,
    ) -> list[T]:
        normalized = {
            part.lower()
            for part in parts
        }

        return [
            item
            for key, item in self._items.items()
            if normalized.issubset(key)
        ]

    def query_regex(
        self,
        pattern: str,
    ) -> list[T]:
        regex = re.compile(
            pattern,
            re.IGNORECASE,
        )

        return [
            item
            for key, item in self._items.items()
            if regex.search(
                self._separator.join(key)
            )
        ]

    def keys(self) -> tuple[str, ...]:
        return tuple(
            self._separator.join(key)
            for key in self._items
        )