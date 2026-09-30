package directory

func ResponseHeaders(requestID string) map[string]string {
	return map[string]string{"X-Request-ID": requestID, "Content-Type": "application/json"}
}
