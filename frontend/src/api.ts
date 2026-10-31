// Utilitários compartilhados pelas telas autenticadas.
export type Lang = 'pt' | 'en';

const locale = (lang: Lang) => (lang === 'pt' ? 'pt-BR' : 'en-US');

/** Formata valores monetários em BRL respeitando o idioma da interface. */
export const money = (value: string | number | null | undefined, lang: Lang) =>
  new Intl.NumberFormat(locale(lang), { style: 'currency', currency: 'BRL' }).format(Number(value ?? 0));

/** Formata percentuais já expressos em pontos (ex.: "12.5" -> "12,5%"). */
export const percent = (value: string | number, lang: Lang, digits = 2) =>
  `${new Intl.NumberFormat(locale(lang), { maximumFractionDigits: digits }).format(Number(value))}%`;

/** Formata datas ISO (AAAA-MM-DD) sem conversão de fuso. */
export const shortDate = (value: string, lang: Lang) => {
  const [year, month, day] = value.slice(0, 10).split('-');
  return lang === 'pt' ? `${day}/${month}/${year}` : `${month}/${day}/${year}`;
};

/** Competência AAAA-MM do mês corrente no fuso de São Paulo (ADR-006). */
export const currentCompetence = () =>
  new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo', year: 'numeric', month: '2-digit' }).format(new Date());

/** Data AAAA-MM-DD de hoje no fuso de São Paulo. */
export const today = () =>
  new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date());

/** Desloca uma competência AAAA-MM em `delta` meses. */
export const shiftCompetence = (competence: string, delta: number) => {
  const [year, month] = competence.split('-').map(Number);
  const date = new Date(Date.UTC(year, month - 1 + delta, 1));
  return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}`;
};

export class RequestError extends Error {}

/** Chamada autenticada à API; dispara o evento de mudança financeira em escritas. */
export async function api<T>(token: string, path: string, options: RequestInit = {}): Promise<T> {
  const method = (options.method ?? 'GET').toUpperCase();
  const headers: Record<string, string> = { Authorization: `Bearer ${token}`, ...(options.headers as Record<string, string>) };
  if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  const response = await fetch(path.startsWith('/api/') ? path : `/api/v1/auth${path}`, {
    credentials: 'same-origin', ...options, headers,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new RequestError(typeof body.detail === 'string' ? body.detail : 'service_unavailable');
  }
  if (method !== 'GET') window.dispatchEvent(new Event('finnova-financial-changed'));
  return (response.status === 204 ? undefined : await response.json()) as T;
}

/** Cabeçalho de idempotência exigido nas criações de lançamento (C-16). */
export const idempotent = () => ({ 'Idempotency-Key': crypto.randomUUID() });

/** Mensagem de erro amigável e bilíngue a partir do código retornado pela API. */
export function errorText(cause: unknown, lang: Lang) {
  const code = cause instanceof Error ? cause.message : '';
  const messages: Record<string, [string, string]> = {
    email_not_verified: ['Confirme seu e-mail para usar esta função.', 'Confirm your email to use this feature.'],
    indicator_unavailable: ['Indicador oficial indisponível no cache local.', 'Official indicator unavailable in the local cache.'],
    not_found: ['Registro não encontrado.', 'Record not found.'],
    invalid_input: ['Revise os dados informados.', 'Please review the data entered.'],
  };
  const [pt, en] = messages[code] ?? ['Não foi possível concluir a operação. Revise os dados e tente novamente.', 'The operation could not be completed. Check the data and try again.'];
  return lang === 'pt' ? pt : en;
}
