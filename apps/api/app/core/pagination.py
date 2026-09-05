from dataclasses import dataclass
from typing import Generic, TypeVar


Item = TypeVar("Item")


@dataclass(frozen=True, slots=True)
class PageRequest:
    page: int = 1
    page_size: int = 20

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("Page must be greater than or equal to 1.")
        if not 1 <= self.page_size <= 100:
            raise ValueError("Page size must be between 1 and 100.")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass(frozen=True, slots=True)
class PageResult(Generic[Item]):
    items: tuple[Item, ...]
    page: int
    page_size: int
    total_items: int

    @property
    def total_pages(self) -> int:
        if self.total_items == 0:
            return 0
        return (self.total_items + self.page_size - 1) // self.page_size

    @property
    def has_next_page(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        return self.page > 1 and self.total_pages > 0


__all__ = ["PageRequest", "PageResult"]
