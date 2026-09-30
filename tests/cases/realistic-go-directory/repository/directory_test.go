package directory

import "testing"

func TestFindExactEmail(t *testing.T) {
	directory := NewDirectory()
	directory.Add(Contact{Email: "Person@Example.com", Name: "Person"})
	if _, ok := directory.Find("person@example.com"); !ok {
		t.Fatal("contact not found")
	}
}
