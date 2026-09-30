def record_retry(audit, headers: dict[str, str], request_id: str) -> None:
    visible_headers = headers.copy()
    visible_headers.pop("Authorization", None)
    audit.write({"event": "retry", "request_id": request_id,
                 "headers": visible_headers})
