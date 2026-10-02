from audit import AuditLog
from sender import Sender
from store import NoticeStore


def dispatch_pending(
    store: NoticeStore, sender: Sender, audit: AuditLog, tenant_id: str
) -> list[str]:
    sent_ids: list[str] = []
    for notice in store.pending(tenant_id):
        sender.send(notice)
        store.mark_sent(notice.id)
        audit.sent(tenant_id, notice.id)
        sent_ids.append(notice.id)
    return sent_ids
