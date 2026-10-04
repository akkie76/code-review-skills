package labels

import "fmt"

func Label(id int) string {
    return fmt.Sprintf("item-%d", id)
}
