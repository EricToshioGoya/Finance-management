import Constants from 'expo-constants';
import { createApi } from './http';

// Mesma API versionada da web (RNF-05, C-11). Clientes nativos não enviam Origin.
const base = (Constants.expoConfig?.extra?.apiUrl as string | undefined) ?? 'https://localhost:8443';

export { ApiError, newIdempotencyKey } from './http';
export const api = createApi(base, (url, init) => fetch(url, init));
