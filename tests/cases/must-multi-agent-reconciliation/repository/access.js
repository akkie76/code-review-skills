export function canView(user, record) {
  return user.id === record.ownerId;
}
