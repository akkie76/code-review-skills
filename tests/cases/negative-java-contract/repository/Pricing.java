final class Pricing {
    static int quote(int grossCents, int discountCents) {
        return grossCents - discountCents;
    }
}
