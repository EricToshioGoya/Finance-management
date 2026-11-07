// Transporte HTTP puro (sem Expo), testável com fetch falso (C-17).

export class ApiError extends Error {}

type Fetch = (url: string, init: RequestInit) => Promise<Response>;

export function createApi(base: string, fetchImpl: Fetch) {
  return async function api<T>(path: string, token: string | null, init: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };
    if (token) headers.Authorization = `Bearer ${token}`;
    if (init.body) headers['Content-Type'] = 'application/json';
    const response = await fetchImpl(`${base}/api/v1${path}`, { ...init, headers });
    if (!response.ok) {
      // Só o código de erro da API chega à tela; detalhe ausente vira erro genérico.
      const body = await response.json().catch(() => ({}));
      throw new ApiError(typeof body.detail === 'string' ? body.detail : 'service_unavailable');
    }
    return (response.status === 204 ? undefined : await response.json()) as T;
  };
}

export const newIdempotencyKey = () =>
  `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;
