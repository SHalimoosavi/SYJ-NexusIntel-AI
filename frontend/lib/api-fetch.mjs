export async function apiFetchWithRefresh(input, init = {}, apiBase, fetcher, refreshSession) {
  const options = {
    ...init,
    credentials: "include",
    cache: init.cache ?? "no-store",
  };
  const firstResponse = await fetcher(input, options);
  const requestUrl = String(input);
  if (
    firstResponse.status !== 401 ||
    requestUrl.includes("/auth/login") ||
    requestUrl.includes("/auth/refresh") ||
    requestUrl.includes("/auth/logout") ||
    requestUrl.includes("/invitations/accept")
  ) {
    return firstResponse;
  }

  const refreshed = await refreshSession(apiBase);
  if (!refreshed) return firstResponse;
  return fetcher(input, options);
}
