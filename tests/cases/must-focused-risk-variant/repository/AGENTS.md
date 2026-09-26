# Value resolution contract

`resolveValue` accepts `None`, strings, and arbitrary caller-provided objects.
Only `None` and the empty string select the default. Every other value must be
returned unchanged without requiring its equality implementation to accept a
string operand.
