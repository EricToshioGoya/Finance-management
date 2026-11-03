// Formatação compartilhada (Decimal chega como string da API; exibição em pt-BR).
export function money(value: string | number | null | undefined): string {
  const number = Number(value ?? 0);
  const [integer, cents] = Math.abs(number).toFixed(2).split('.');
  const grouped = integer.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${number < 0 ? '-' : ''}R$ ${grouped},${cents}`;
}

/** Data civil AAAA-MM-DD no fuso America/Sao_Paulo (C-15, ADR-006). */
export function today(now: Date = new Date()): string {
  try {
    const parts = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Sao_Paulo', year: 'numeric', month: '2-digit', day: '2-digit',
    }).formatToParts(now);
    const part = (type: string) => parts.find(item => item.type === type)?.value ?? '';
    return `${part('year')}-${part('month')}-${part('day')}`;
  } catch {
    // Motor JS sem base de fusos: São Paulo está em UTC-3 fixo desde 2019 (sem horário de verão).
    return new Date(now.getTime() - 3 * 60 * 60 * 1000).toISOString().slice(0, 10);
  }
}

/** Competência AAAA-MM do mês corrente no fuso America/Sao_Paulo. */
export function currentCompetence(now: Date = new Date()): string {
  return today(now).slice(0, 7);
}

/**
 * Converte o valor digitado (pt-BR: "1.234,56"; ou "1234.56") para o decimal da API ("1234.56").
 * Devolve null quando o texto não é um valor monetário válido com até 2 casas.
 */
export function parseAmount(input: string): string | null {
  let text = input.replace(/R\$|\s/g, '');
  if (text.includes(',')) text = text.replace(/\./g, '').replace(',', '.');
  return /^\d+(\.\d{1,2})?$/.test(text) ? text : null;
}
