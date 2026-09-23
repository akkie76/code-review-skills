export function loadConfig(env) {
  return { token: env.API_TOKEN ?? null };
}
