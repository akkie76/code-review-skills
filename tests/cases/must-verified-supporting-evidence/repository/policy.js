export function canEdit(user, record) {
  return user.id === record.ownerId;
}
