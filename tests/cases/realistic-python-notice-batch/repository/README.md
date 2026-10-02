# Tenant notice delivery

`dispatch_pending` sends all pending notices for one tenant and returns the
IDs sent in delivery order. A successfully sent notice is marked sent, then
recorded in the audit log. If the sender fails, that notice stays pending.

The store is in memory so the fixture can be exercised without a database.
Pending notices are ordered by ID; tenant boundaries are enforced by the
store. A batch may contain more notices than one page.
