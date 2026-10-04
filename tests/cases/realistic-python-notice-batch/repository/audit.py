class AuditLog:
    def __init__(self) -> None:
        self.events: list[dict[str, str]] = []

    def sent(self, tenant_id: str, notice_id: str) -> None:
        self.events.append({
            "event": "notice.sent",
            "tenant_id": tenant_id,
            "notice_id": notice_id,
        })
