import Constants from 'expo-constants';

// Mesma API versionada da web (RNF-05, C-11). Clientes nativos não enviam Origin.
const base = (Constants.expoConfig?.extra?.apiUrl as string | undefined) ?? 'https://localhost:8443';

export class ApiError extends Error {}

export async function api<T>(path: string, token: string | null, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };
  if (token) headers.Authorization = `Bearer ${token}`;
  if (init.body) headers['Content-Type'] = 'application/json';
  const response = await fetch(`${base}/api/v1${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(typeof body.detail === 'string' ? body.detail : 'service_unavailable');
  }
  return (response.status === 204 ? undefined : await response.json()) as T;
}

export const newIdempotencyKey = () =>
  `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;
