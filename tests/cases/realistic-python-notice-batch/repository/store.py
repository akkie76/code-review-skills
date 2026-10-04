from model import Notice


class NoticeStore:
    def __init__(self, notices: list[Notice]) -> None:
        self.notices = {notice.id: notice for notice in notices}

    def pending(self, tenant_id: str) -> list[Notice]:
        return sorted(
            (
                notice for notice in self.notices.values()
                if notice.tenant_id == tenant_id and not notice.sent
            ),
            key=lambda notice: notice.id,
        )

    def mark_sent(self, notice_id: str) -> None:
        self.notices[notice_id].sent = True
