import test from "node:test";
import assert from "node:assert/strict";
import { cancelPendingAuthRefresh, refreshAuthSession, resumeAuthRefresh } from "./auth-refresh.mjs";

function deferred() {
  let resolve;
  const promise = new Promise((done) => { resolve = done; });
  return { promise, resolve };
}

test("parallel calls in one tab share exactly one refresh request", async () => {
  resumeAuthRefresh();
  const gate = deferred();
  let calls = 0;
  const fetcher = async () => { calls += 1; await gate.promise; return { ok: true }; };
  const first = refreshAuthSession("/api", fetcher, undefined);
  const second = refreshAuthSession("/api", fetcher, undefined);
  gate.resolve();
  assert.deepEqual(await Promise.all([first, second]), [true, true]);
  assert.equal(calls, 1);
});

test("refresh failure is propagated without reporting success", async () => {
  resumeAuthRefresh();
  const result = await refreshAuthSession("/api", async () => ({ ok: false }), undefined);
  assert.equal(result, false);
});

test("logout during an in-flight refresh prevents it from reviving auth state", async () => {
  resumeAuthRefresh();
  const gate = deferred();
  const pending = refreshAuthSession("/api", async () => {
    await gate.promise;
    return { ok: true };
  }, undefined);
  cancelPendingAuthRefresh();
  gate.resolve();
  assert.equal(await pending, false);
  assert.equal(await refreshAuthSession("/api", async () => ({ ok: true }), undefined), false);
  resumeAuthRefresh();
});

test("cross-tab Web Lock is used for refresh serialization", async () => {
  resumeAuthRefresh();
  let lockName = "";
  const locks = {
    request: async (name, callback) => { lockName = name; return callback(); },
  };
  const result = await refreshAuthSession("/api", async () => ({ ok: true }), locks);
  assert.equal(result, true);
  assert.equal(lockName, "syj-auth-refresh");
});

test("independent module contexts serialize refresh through shared Web Locks and storage", async () => {
  const originalStorage = globalThis.localStorage;
  const values = new Map();
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    value: {
      getItem: (key) => values.get(key) ?? null,
      setItem: (key, value) => values.set(key, value),
    },
  });
  try {
    const firstContext = await import("./auth-refresh.mjs?context=first");
    const secondContext = await import("./auth-refresh.mjs?context=second");
    firstContext.resumeAuthRefresh();
    secondContext.resumeAuthRefresh();
    let active = false;
    const queue = [];
    const locks = {
      request: async (_name, callback) => {
        if (active) await new Promise((resolve) => queue.push(resolve));
        active = true;
        try { return await callback(); }
        finally { active = false; queue.shift()?.(); }
      },
    };
    let refreshCalls = 0;
    const fetcher = async () => {
      refreshCalls += 1;
      await new Promise((resolve) => setTimeout(resolve, 5));
      return { ok: true };
    };
    const results = await Promise.all([
      firstContext.refreshAuthSession("/api", fetcher, locks),
      secondContext.refreshAuthSession("/api", fetcher, locks),
    ]);
    assert.deepEqual(results, [true, true]);
    assert.equal(refreshCalls, 1);
  } finally {
    if (originalStorage === undefined) delete globalThis.localStorage;
    else Object.defineProperty(globalThis, "localStorage", { configurable: true, value: originalStorage });
  }
});

test("refresh coordinator resumes after successful authentication", async () => {
  cancelPendingAuthRefresh();
  resumeAuthRefresh();
  const result = await refreshAuthSession(
    "/api",
    async () => ({ ok: true }),
    undefined,
  );
  assert.equal(result, true);
});
