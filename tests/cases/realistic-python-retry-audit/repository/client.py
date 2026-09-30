from audit import record_retry


class TransportTimeout(Exception):
    pass


def reserve(transport, audit, request_id: str, sku: str, quantity: int) -> dict:
    headers = {"Content-Type": "application/json", "Idempotency-Key": request_id}
    payload = {"sku": sku, "quantity": quantity}

    for attempt in range(2):
        try:
            return transport.post("/reservations", payload, headers)
        except TransportTimeout:
            if attempt == 1:
                raise
            record_retry(audit, headers.copy())

    raise AssertionError("unreachable")
