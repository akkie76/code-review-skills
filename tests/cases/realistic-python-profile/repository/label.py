def label(item: dict[str, str]) -> str:
    name = item["name"].strip()
    return f'{name} ({item["id"]})'
