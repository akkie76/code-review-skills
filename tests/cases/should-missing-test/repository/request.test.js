import { request } from "./request.js";

it("returns the response", async () => {
  await expect(request(async () => "ok")).resolves.toBe("ok");
});
