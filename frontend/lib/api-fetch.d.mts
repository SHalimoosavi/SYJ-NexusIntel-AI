export function apiFetchWithRefresh(
  input: RequestInfo | URL,
  init: RequestInit,
  apiBase: string,
  fetcher: typeof fetch,
  refreshSession: (apiBase: string) => Promise<boolean>,
): Promise<Response>;
