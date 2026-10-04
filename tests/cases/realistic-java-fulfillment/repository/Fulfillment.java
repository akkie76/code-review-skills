import java.io.IOException;

final class Fulfillment {
    private final OrderStore store;
    private final ShipmentNotice notices;

    Fulfillment(OrderStore store, ShipmentNotice notices) {
        this.store = store;
        this.notices = notices;
    }

    void fulfill(Order order) throws IOException {
        store.save(order);
        notices.sent(order.id());
    }
}
