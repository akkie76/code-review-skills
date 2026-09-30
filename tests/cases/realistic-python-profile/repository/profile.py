from tags import clean_tags


def primary_tag(values: list[str]) -> str | None:
    tags = clean_tags(values)
    return tags[0] if tags else None
