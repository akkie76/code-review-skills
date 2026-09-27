function decode(text) {
  return JSON.parse(text);
}

export function loadConfig(text) {
  return decode(text);
}
