package records

import "testing"

func TestCount(t *testing.T) {
	if Count(nil) != 0 || Count([]string{"a", "b"}) != 2 {
		t.Fatal("unexpected count")
	}
}
