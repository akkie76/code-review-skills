final class RetryPolicy {
    private final int maxAttempts;

    RetryPolicy(int maxAttempts) {
        this.maxAttempts = maxAttempts;
    }

    boolean shouldRetry(int completedAttempts) {
        return completedAttempts < maxAttempts;
    }
}
