// Formatação compartilhada (Decimal chega como string da API; exibição em pt-BR).
export function money(value: string | number | null | undefined): string {
  const number = Number(value ?? 0);
  const [integer, cents] = Math.abs(number).toFixed(2).split('.');
  const grouped = integer.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${number < 0 ? '-' : ''}R$ ${grouped},${cents}`;
}

/** Competência AAAA-MM do mês corrente no fuso de São Paulo (ADR-006: UTC-3, sem horário de verão). */
export function currentCompetence(now: Date = new Date()): string {
  const local = new Date(now.getTime() - 3 * 60 * 60 * 1000);
  return `${local.getUTCFullYear()}-${String(local.getUTCMonth() + 1).padStart(2, '0')}`;
}

export function today(now: Date = new Date()): string {
  const local = new Date(now.getTime() - 3 * 60 * 60 * 1000);
  return local.toISOString().slice(0, 10);
}
