def format_receipt(sku: str, quantity: int, reference: str) -> str:
    return "Reserved " + str(quantity) + " x " + sku + " (" + reference + ")"


def format_line(sku: str, quantity: int) -> str:
    return str(quantity) + " x " + sku
