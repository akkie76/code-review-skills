def summary_line(tenant_id: str, sent_ids: list[str]) -> str:
    count = len(sent_ids)
    return tenant_id + ": sent " + str(count) + " notice(s)"


def id_line(sent_ids: list[str]) -> str:
    return ", ".join(sent_ids) if sent_ids else "none"
