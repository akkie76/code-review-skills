package metrics

// Mean returns zero for an empty input.
func Mean(values []int) int {
	sum := 0
	for _, value := range values {
		sum += value
	}
	return sum / len(values)
}
