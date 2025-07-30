def shared_items(list_one, list_two):
    """
    Return the list of items that are shared
    between two lists
    """

    return [x for x in list_one.keys() if x in list_two]


def sanitize_like_input(raw: str) -> str:
    """Escape special characters used in SQL LIKE"""
    escaped = raw.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return escaped
