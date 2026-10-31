import { useCallback, useEffect, useState } from 'react';

type Point = {
  competence: string;
  total_assets: string;
  total_liabilities: string;
  net_worth: string;
  captured_at: string;
};
type Series = 'total_assets' | 'total_liabilities' | 'net_worth';
const series: { key: Series; pt: string; en: string; color: string }[] = [
  { key: 'total_assets', pt: 'Ativos', en: 'Assets', color: '#16806c' },
  { key: 'total_liabilities', pt: 'Passivos', en: 'Liabilities', color: '#b45309' },
  { key: 'net_worth', pt: 'Patrimônio líquido', en: 'Net worth', color: '#2563eb' },
];
const money = (value: string | number, lang: 'pt' | 'en') =>
  new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency: 'BRL',
  }).format(Number(value));

export function NetWorthHistory({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const [points, setPoints] = useState<Point[]>([]);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [visible, setVisible] = useState<Series[]>(series.map(item => item.key));
  const pt = lang === 'pt';
  const headers = { Authorization: 'Bearer ' + token };

  const load = useCallback(async (from: string, to: string) => {
    setLoading(true); setError('');
    try {
      const query = new URLSearchParams();
      if (from) query.set('start', from + '-01');
      if (to) query.set('end', to + '-01');
      const response = await fetch('/api/v1/auth/financial/net-worth/history?' + query, {
        headers: { Authorization: 'Bearer ' + token },
      });
      if (!response.ok) throw new Error(String(response.status));
      setPoints(await response.json() as Point[]);
    } catch {
      setError(pt ? 'Não foi possível carregar o histórico.' : 'Could not load history.');
    } finally { setLoading(false); }
  }, [token, pt]);

  useEffect(() => { void load('', ''); }, [load]);

  async function capture() {
    setLoading(true); setError(''); setNotice('');
    try {
      const response = await fetch('/api/v1/auth/financial/net-worth/history/snapshots', {
        method: 'POST', headers,
      });
      if (!response.ok) throw new Error(String(response.status));
      setNotice(pt ? 'Posição mensal registrada. Repetir não altera a posição.' : 'Monthly position saved. Repeating does not change it.');
      await load(start, end);
    } catch {
      setError(pt ? 'Não foi possível registrar a posição.' : 'Could not save the position.');
    } finally { setLoading(false); }
  }

  const values = points.flatMap(point => visible.map(key => Number(point[key])));
  const low = Math.min(0, ...values);
  const high = Math.max(1, ...values);
  const x = (index: number) => 54 + (points.length < 2 ? 290 : index * 580 / (points.length - 1));
  const y = (value: number) => 205 - (value - low) / (high - low || 1) * 175;
  return <section className="profile" aria-labelledby="net-worth-history-title">
    <h3 id="net-worth-history-title">{pt ? 'Evolução do patrimônio real' : 'Real net worth history'}</h3>
    <p>{pt ? 'Posições mensais registradas, sem simulações nem preenchimento de meses ausentes.' : 'Saved monthly positions, excluding projections and missing months.'}</p>
    <div className="history-controls">
      <label>{pt ? 'De' : 'From'} <input aria-label={pt ? 'Mês inicial' : 'Start month'} type="month" value={start} onChange={event => setStart(event.target.value)} /></label>
      <label>{pt ? 'Até' : 'To'} <input aria-label={pt ? 'Mês final' : 'End month'} type="month" value={end} onChange={event => setEnd(event.target.value)} /></label>
      <button type="button" disabled={loading || (!!start && !!end && start > end)} onClick={() => void load(start, end)}>{pt ? 'Filtrar' : 'Filter'}</button>
      <button type="button" className="secondary" disabled={loading} onClick={() => void capture()}>{pt ? 'Registrar posição deste mês' : 'Capture this month'}</button>
    </div>
    <div className="history-controls" role="group" aria-label={pt ? 'Séries visíveis' : 'Visible series'}>
      {series.map(item => <label key={item.key}>
        <input type="checkbox" checked={visible.includes(item.key)}
          onChange={event => setVisible(current => event.target.checked ? [...current, item.key] : current.filter(key => key !== item.key))} />
        {pt ? item.pt : item.en}
      </label>)}
    </div>
    {loading && <p role="status">{pt ? 'Carregando…' : 'Loading…'}</p>}
    {error && <p role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
    {points.length === 0 ? <p>{pt ? 'Nenhuma posição registrada no intervalo.' : 'No saved positions in this interval.'}</p> : <>
      <svg viewBox="0 0 680 260" role="img" aria-label={pt ? 'Gráfico de linhas da evolução mensal dos ativos, passivos e patrimônio líquido' : 'Line chart of monthly assets, liabilities and net worth'} style={{ width: '100%', maxWidth: 680 }}>
        {[0, 0.5, 1].map(tick => <g key={tick}>
          <line x1="54" x2="634" y1={205 - tick * 175} y2={205 - tick * 175} stroke="currentColor" opacity="0.15" />
          <text x="48" y={210 - tick * 175} textAnchor="end" fill="currentColor" fontSize="11">{Math.round(low + tick * (high - low)).toLocaleString(pt ? 'pt-BR' : 'en-US')}</text>
        </g>)}
        {series.filter(item => visible.includes(item.key)).map(item => <g key={item.key}>
          <polyline fill="none" stroke={item.color} strokeWidth="3" points={points.map((point, index) => `${x(index)},${y(Number(point[item.key]))}`).join(' ')} />
          {points.map((point, index) => <circle key={point.competence} cx={x(index)} cy={y(Number(point[item.key]))} r="4" fill={item.color}><title>{point.competence.slice(0, 7)}: {money(point[item.key], lang)}</title></circle>)}
        </g>)}
        {points.map((point, index) => <text key={point.competence} x={x(index)} y="231" textAnchor="middle" fill="currentColor" fontSize="11">{point.competence.slice(0, 7)}</text>)}
      </svg>
      <div className="indicator-table-wrap" tabIndex={0}><table>
        <caption>{pt ? 'Valores exatos das posições registradas (BRL)' : 'Exact saved positions (BRL)'}</caption>
        <thead><tr><th>{pt ? 'Mês' : 'Month'}</th>{series.map(item => <th key={item.key}>{pt ? item.pt : item.en}</th>)}</tr></thead>
        <tbody>{points.map(point => <tr key={point.competence}><th scope="row">{point.competence.slice(0, 7)}</th>{series.map(item => <td key={item.key}>{money(point[item.key], lang)}</td>)}</tr>)}</tbody>
      </table></div>
    </>}
  </section>;
}
