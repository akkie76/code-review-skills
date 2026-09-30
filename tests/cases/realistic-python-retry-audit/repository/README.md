# Inventory reservation client

`reserve` submits one reservation and retries a timeout once. The caller
provides a stable `request_id` for the reservation. The remote service uses
that ID as an idempotency key to prevent duplicate reservations when the
first request may have succeeded.

An audit event is written before retrying. The audit trail must not contain
the idempotency key. Receipt and attempt summaries are for display only.
