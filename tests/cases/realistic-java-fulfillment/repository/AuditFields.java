import java.util.Map;

final class AuditFields {
    Map<String, String> forOrder(Order order) {
        return Map.of("order_id", order.id(), "customer", order.customerEmail());
    }
}
