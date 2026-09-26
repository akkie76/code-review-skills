import { normalizeItems } from "./normalize.js";

export function reportCount(records) {
  return normalizeItems(records).length;
}
