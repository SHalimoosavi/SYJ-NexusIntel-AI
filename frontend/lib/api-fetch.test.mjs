import test from "node:test";
import assert from "node:assert/strict";
import { apiFetchWithRefresh } from "./api-fetch.mjs";

test("replays the original protected request exactly once after refresh succeeds", async () => {
  const calls = [];
  const responses = [{ status: 401, ok: false }, { status: 200, ok: true }];
  const fetcher = async (input, init) => {
    calls.push({ input, init });
    return responses.shift();
  };
  let refreshCalls = 0;
  const result = await apiFetchWithRefresh(
    "/protected/resource",
    { method: "POST", body: "payload" },
    "/api",
    fetcher,
    async () => { refreshCalls += 1; return true; },
  );
  assert.equal(result.status, 200);
  assert.equal(refreshCalls, 1);
  assert.equal(calls.length, 2);
  assert.deepEqual(calls[0], calls[1]);
});

test("does not replay when refresh fails", async () => {
  let calls = 0;
  const result = await apiFetchWithRefresh(
    "/protected/resource",
    {},
    "/api",
    async () => { calls += 1; return { status: 401, ok: false }; },
    async () => false,
  );
  assert.equal(result.status, 401);
  assert.equal(calls, 1);
});

test("does not refresh authentication endpoints", async () => {
  let refreshCalls = 0;
  const result = await apiFetchWithRefresh(
    "/auth/refresh",
    {},
    "/api",
    async () => ({ status: 401, ok: false }),
    async () => { refreshCalls += 1; return true; },
  );
  assert.equal(result.status, 401);
  assert.equal(refreshCalls, 0);
});
