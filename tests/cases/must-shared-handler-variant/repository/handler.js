export function route(event, session, send) {
  switch (event.kind) {
    case "member":
      return send(event);
    case "guest":
      if (!session.authorized) return "blocked";
      return send(event);
    default:
      return "unsupported";
  }
}
