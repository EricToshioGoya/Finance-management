import { useCallback, useEffect, useState } from 'react';

type Item = {
  id: string;
  kind: 'asset' | 'liability';
  name: string;
  value: string;
  annual_rate: string | null;
  origin: 'manual' | 'account' | 'credit_card_invoice';
};
type Payload = { as_of: string; items: Item[]; total_absolute: string };
type Filter = 'all' | 'asset' | 'liability';
const money = (number: number, lang: 'pt' | 'en') =>
  new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency: 'BRL',
  }).format(number);

/** Rates are display scales, not estimated returns or new financial facts. */
export function heatmapColor(item: Item): string {
  const rate = item.annual_rate === null ? null : Number(item.annual_rate);
  if (rate === null || !Number.isFinite(rate)) return '#88919c';
  if (item.kind === 'asset') {
    if (rate <= 0) return '#d5e8db';
    const intensity = Math.min(rate / 20, 1);
    return `hsl(145 53% ${Math.round(78 - intensity * 50)}%)`;
  }
  const intensity = Math.max(0, Math.min(rate / 20, 1));
  return `hsl(${Math.round(48 - intensity * 46)} 80% ${Math.round(75 - intensity * 32)}%)`;
}
export function heatmapRows(items: Item[], filter: Filter) {
  const visible = items.filter(item => filter === 'all' || item.kind === filter);
  const total = visible.reduce((sum, item) => sum + Math.abs(Number(item.value)), 0);
  return visible.map(item => ({
    ...item,
    amount: Math.abs(Number(item.value)),
    percentage: total > 0 ? (Math.abs(Number(item.value)) / total) * 100 : 0,
  }));
}

export function NetWorthHeatmap({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [position, setPosition] = useState<Payload | null>(null);
  const [filter, setFilter] = useState<Filter>('all');
  const [selected, setSelected] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/auth/financial/net-worth/heatmap', {
        headers: { Authorization: 'Bearer ' + token },
      });
      if (!response.ok) throw new Error('heatmap_unavailable');
      setPosition(await response.json() as Payload);
      setError(false);
    } catch {
      setError(true);
    } finally { setLoading(false); }
  }, [token]);

  useEffect(() => {
    void load();
    const refresh = () => { if (document.visibilityState === 'visible') void load(); };
    const interval = window.setInterval(refresh, 30000);
    window.addEventListener('focus', refresh);
    document.addEventListener('visibilitychange', refresh);
    window.addEventListener('finnova-financial-changed', refresh);
    return () => {
      window.clearInterval(interval);
      window.removeEventListener('focus', refresh);
      document.removeEventListener('visibilitychange', refresh);
      window.removeEventListener('finnova-financial-changed', refresh);
    };
  }, [load]);

  const rows = heatmapRows(position?.items ?? [], filter);
  const occupied = rows.filter(item => item.amount > 0);
  const chosen = rows.find(item => item.id === selected);
  const label = (item: Item) => item.kind === 'asset'
    ? pt ? 'Ativo' : 'Asset' : pt ? 'Passivo' : 'Liability';
  const rateLabel = (item: Item) => item.kind === 'asset'
    ? pt ? 'Rentabilidade anual informada' : 'Reported annual return'
    : pt ? 'Taxa anual de juros' : 'Annual interest rate';

  return <section className="profile" aria-labelledby="patrimony-heatmap-title">
    <h3 id="patrimony-heatmap-title">{pt ? 'Mapa de calor patrimonial' : 'Net worth heatmap'}</h3>
    <p>{pt
      ? 'Tamanho proporcional ao valor absoluto. Verde: rentabilidade informada; amarelo a vermelho: juros da dívida; cinza: taxa não disponível.'
      : 'Area represents absolute value. Green: reported return; yellow to red: debt interest; grey: rate unavailable.'}</p>
    <fieldset className="heatmap-filters">
      <legend>{pt ? 'Exibir' : 'Show'}</legend>
      {(['all', 'asset', 'liability'] as Filter[]).map(value =>
        <label key={value}>
          <input type="radio" name="heatmap-filter" checked={filter === value}
            onChange={() => { setFilter(value); setSelected(null); }} />
          {value === 'all' ? pt ? 'Todos' : 'All' : value === 'asset'
            ? pt ? 'Somente ativos' : 'Assets only' : pt ? 'Somente passivos' : 'Liabilities only'}
        </label>)}
    </fieldset>
    {loading && <p role="status">{pt ? 'Carregando patrimônio…' : 'Loading net worth…'}</p>}
    {error && <p role="alert">{pt ? 'Não foi possível atualizar o mapa.' : 'Could not refresh heatmap.'}
      <button type="button" onClick={() => void load()}>{pt ? 'Tentar novamente' : 'Retry'}</button></p>}
    {!loading && !error && occupied.length === 0 && <p role="status">
      {pt ? 'Sem valores patrimoniais positivos ou negativos neste filtro.' : 'No nonzero positions in this filter.'}
    </p>}
    {occupied.length > 0 && <div aria-label={pt ? 'Mapa de calor do patrimônio real' : 'Real net worth heatmap'}
      className="heatmap-chart" style={{ display: 'flex', height: 190, width: '100%', overflow: 'hidden', gap: 2 }}>
      {occupied.map(item => <button type="button" key={item.id}
        style={{ flex: `${item.amount} 1 0`, minWidth: 0, padding: 2, overflow: 'hidden',
          backgroundColor: heatmapColor(item), color: '#17212b', border: selected === item.id ? '3px solid #000' : '1px solid #555' }}
        title={`${item.name} · ${label(item)} · ${money(Number(item.value), lang)} · ${rateLabel(item)}: ${item.annual_rate ?? (pt ? 'não informado' : 'not available')}`}
        aria-label={`${item.name}: ${money(Number(item.value), lang)}, ${item.percentage.toFixed(1)}%, ${label(item)}`}
        aria-pressed={selected === item.id}
        onClick={() => setSelected(current => current === item.id ? null : item.id)}>
        <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', fontSize: 12 }}>
          {item.percentage >= 12 ? item.name : '·'}
        </span>
      </button>)}
    </div>}
    {chosen && <p role="status"><strong>{chosen.name}</strong> — {label(chosen)}; {money(Number(chosen.value), lang)};
      {' '}{chosen.percentage.toFixed(1)}%; {rateLabel(chosen)}: {chosen.annual_rate === null
        ? pt ? 'não informado' : 'not available' : chosen.annual_rate + '%'}.
    </p>}
    {rows.length > 0 && <div className="indicator-table-wrap"><table>
      <caption>{pt ? 'Dados acessíveis do mapa de calor' : 'Accessible heatmap values'}</caption>
      <thead><tr><th>{pt ? 'Nome' : 'Name'}</th><th>{pt ? 'Tipo' : 'Type'}</th>
        <th>{pt ? 'Valor (BRL)' : 'Amount (BRL)'}</th><th>%</th>
        <th>{pt ? 'Indicador anual' : 'Annual rate'}</th></tr></thead>
      <tbody>{rows.map(item => <tr key={item.id}>
        <th scope="row">{item.name}</th><td>{label(item)}</td>
        <td>{money(Number(item.value), lang)}</td><td>{item.percentage.toFixed(1)}%</td>
        <td>{item.annual_rate === null ? pt ? 'Não informado' : 'Not available' : item.annual_rate + '%'}</td>
      </tr>)}</tbody>
    </table></div>}
    <small>{pt
      ? 'Cores usam escala ilustrativa limitada a 20% ao ano; valores sem taxa não recebem rentabilidade presumida. Apenas patrimônio real, sem simulações.'
      : 'Colors use an illustrative annual scale capped at 20%; missing rates are never estimated. Real positions only, no simulations.'}</small>
  </section>;
}
