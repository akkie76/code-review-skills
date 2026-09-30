import java.util.Locale;

final class ReceiptFormatter {
    String render(Order order) {
        String amount = String.format(Locale.US, "%.2f", order.amountCents() / 100.0);
        String identity = "Order " + order.id();
        String recipient = " for " + order.customerEmail();
        return identity + recipient + ": $" + amount;
    }
}
