def clean_tags(values: list[str]) -> list[str]:
    return [value.strip() for value in values if value.strip()]
