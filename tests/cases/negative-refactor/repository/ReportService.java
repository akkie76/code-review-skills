import java.util.List;

final class ReportService {
    String summarize(List<Integer> amounts) {
        int count = amounts.size();
        int total = 0;
        int min = 0;
        int max = 0;
        for (int i = 0; i < count; i++) {
            int amount = amounts.get(i);
            total += amount;
            if (i == 0 || amount < min) {
                min = amount;
            }
            if (i == 0 || amount > max) {
                max = amount;
            }
        }
        String status = count == 0 ? "empty" : "ready";
        return status + ":" + count + ":" + total + ":" + min + ":" + max;
    }
}
