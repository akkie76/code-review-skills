package directory

import "strings"

func contactKey(raw string) string {
	return strings.ToLower(strings.TrimSpace(raw))
}
