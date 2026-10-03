final class Checkout {
    int charge(int grossCents, int discountCents) {
        return Pricing.quote(grossCents, discountCents);
    }
}
