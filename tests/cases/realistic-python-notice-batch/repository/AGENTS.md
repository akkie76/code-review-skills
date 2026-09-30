# Project guidance

This Python 3.11 service sends tenant-scoped notices. A successful batch must
visit every notice that was pending for the tenant when the batch started,
without sending another tenant's notices. `mark_sent` removes a notice from
subsequent pending queries. The sender can raise `DeliveryError`; a failed
notice must remain pending. The audit log records sent notices and batch
boundaries but does not control delivery.

Display formatting and summary output are not delivery decisions.
