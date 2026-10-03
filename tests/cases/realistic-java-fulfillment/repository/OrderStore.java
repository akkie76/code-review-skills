import java.io.IOException;

interface OrderStore {
    void save(Order order) throws IOException;
}
