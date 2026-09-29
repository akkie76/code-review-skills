package records

func Count(records []string) int {
	if records == nil {
		return 0
	}
	return len(records)
}
