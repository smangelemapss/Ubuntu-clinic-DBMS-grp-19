"""Clamp pagination query params to safe bounds (protects DB from huge OFFSET/FETCH)."""

DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100


def normalize_pagination(page, per_page, *, default_per_page=DEFAULT_PER_PAGE, max_per_page=MAX_PER_PAGE):
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = DEFAULT_PAGE
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = default_per_page

    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))
    return page, per_page
