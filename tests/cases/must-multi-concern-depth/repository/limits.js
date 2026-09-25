export function validateLimit(value) {
  if (!Number.isInteger(value)) throw new TypeError("limit must be an integer");
  return value;
}
