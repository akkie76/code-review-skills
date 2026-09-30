def record_retry(audit, headers: dict[str, str]) -> None:
    visible_headers = headers.copy()
    visible_headers.pop("Authorization", None)
    audit.write({"event": "retry", "headers": visible_headers})
