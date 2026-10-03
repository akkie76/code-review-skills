final class Receipt {
    String render(int grossCents, int discountCents) {
        int net = Pricing.quote(grossCents, discountCents);
        return "Total: " + net;
    }
}
