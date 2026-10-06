# Request contract

`send` performs an idempotent read and is safe to retry. A rejection whose
`code` is `"TIMEOUT"` is retried, with at most three total attempts. Return the
first successful result. If all three attempts time out, reject with the exact
reason from the final attempt.

Other rejection reasons propagate unchanged without retrying. Rejection
reasons are not restricted to Error objects and may include `null` or
`undefined`.
