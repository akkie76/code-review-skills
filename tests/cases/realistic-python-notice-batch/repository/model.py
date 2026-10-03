from dataclasses import dataclass


@dataclass
class Notice:
    id: str
    tenant_id: str
    recipient: str
    subject: str
    body: str
    sent: bool = False
