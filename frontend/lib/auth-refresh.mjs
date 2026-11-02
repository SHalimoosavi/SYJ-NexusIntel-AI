let inFlightRefresh = null;
let authGeneration = 0;
let refreshEnabled = true;
let lastCrossTabRefresh = 0;

const channel = typeof BroadcastChannel === "undefined"
  ? null
  : new BroadcastChannel("syj-auth-refresh");

if (channel) {
  channel.addEventListener("message", (event) => {
    if (event.data && event.data.type === "refresh-complete") {
      lastCrossTabRefresh = Math.max(lastCrossTabRefresh, Number(event.data.at) || 0);
    }
  });
}

function readSharedRefreshTime() {
  let stored = 0;
  try {
    stored = Number(globalThis.localStorage?.getItem("syj-auth-refresh-at") || 0);
  } catch {
    // Storage can be unavailable in hardened browser contexts.
  }
  return Math.max(lastCrossTabRefresh, stored);
}

export function cancelPendingAuthRefresh() {
  authGeneration += 1;
  refreshEnabled = false;
}

export function resumeAuthRefresh() {
  authGeneration += 1;
  refreshEnabled = true;
}

export function refreshAuthSession(apiBase, fetcher = globalThis.fetch, lockManager = globalThis.navigator?.locks) {
  if (!refreshEnabled) return Promise.resolve(false);
  if (inFlightRefresh) return inFlightRefresh;

  const generation = authGeneration;
  const startedAt = Date.now();
  const performRefresh = async () => {
    if (!refreshEnabled || generation !== authGeneration) return false;
    if (readSharedRefreshTime() > startedAt) return true;

    const response = await fetcher(`${apiBase}/auth/refresh`, {
      method: "POST",
      credentials: "include",
      cache: "no-store",
    });
    if (!response.ok || !refreshEnabled || generation !== authGeneration) return false;

    const completedAt = Date.now() + 1;
    lastCrossTabRefresh = completedAt;
    try {
      globalThis.localStorage?.setItem("syj-auth-refresh-at", String(completedAt));
    } catch {
      // Web Locks still serialize refreshes when storage is unavailable.
    }
    channel?.postMessage({ type: "refresh-complete", at: completedAt });
    return true;
  };

  const work = lockManager?.request
    ? lockManager.request("syj-auth-refresh", performRefresh)
    : performRefresh();

  inFlightRefresh = Promise.resolve(work).finally(() => {
    inFlightRefresh = null;
  });
  return inFlightRefresh;
}
