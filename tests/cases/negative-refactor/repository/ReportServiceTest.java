import java.util.List;

final class ReportServiceTest {
    void examples() {
        ReportService service = new ReportService();
        assert service.summarize(List.of()).equals("empty:0:0:0:0");
        assert service.summarize(List.of(2, 3)).equals("ready:2:5:2:3");
    }
}
