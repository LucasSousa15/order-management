from pydantic import BaseModel

from app.core.pagination import PageResult


class PaginationMetaViewModel(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool

    @classmethod
    def from_page(cls, page: PageResult[object]) -> "PaginationMetaViewModel":
        return cls(
            page=page.page,
            page_size=page.page_size,
            total_items=page.total_items,
            total_pages=page.total_pages,
            has_next_page=page.has_next_page,
            has_previous_page=page.has_previous_page,
        )


__all__ = ["PaginationMetaViewModel"]
