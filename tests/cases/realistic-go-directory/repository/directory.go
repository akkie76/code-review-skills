package directory

import "strings"

type Contact struct {
	Email string
	Name  string
}

type Directory struct {
	contacts map[string]Contact
}

func NewDirectory() *Directory {
	return &Directory{contacts: make(map[string]Contact)}
}

func (d *Directory) Add(contact Contact) {
	key := strings.ToLower(strings.TrimSpace(contact.Email))
	d.contacts[key] = contact
}

func (d *Directory) Find(raw string) (Contact, bool) {
	contact, ok := d.contacts[contactKey(raw)]
	return contact, ok
}
