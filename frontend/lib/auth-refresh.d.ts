export function cancelPendingAuthRefresh(): void;
export function resumeAuthRefresh(): void;
export function refreshAuthSession(
  apiBase: string,
  fetcher?: typeof fetch,
  lockManager?: { request: (name: string, callback: () => Promise<boolean>) => Promise<boolean> } | undefined
): Promise<boolean>;
