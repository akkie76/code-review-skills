# Review context

This Python 3.11 package sends inventory reservations to a remote service.
The service deduplicates retries only when every attempt for one reservation
carries the same `Idempotency-Key`. A retry can follow a transport timeout:
the first attempt may have been accepted even when the client saw no response.
An audit event is recorded between attempts and must not expose the key.

`format_receipt` and `summarize_attempts` are display-only helpers. They do
not decide whether a reservation succeeded or whether a retry is safe.
