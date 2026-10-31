import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, errorText, money, percent, shortDate, type Lang } from './api';

type SeriesRow = { month: number; opening_balance: string; contribution: string; interest: string; closing_balance: string };
type Projection = { invested: string; interest: string; gross_amount: string; monthly_series: SeriesRow[]; rate_explanation: string; investor_guidance: string | null; tax_rate?: string; estimated_tax?: string; net_amount?: string };
type Simulation = { id: string; kind: string; label: string; final_amount: string; created_at: string; payload: Record<string, unknown> };
type Comparison = { simulations: Simulation[]; difference_from_first: string[] };
type Indicator = { code: string; value: string; unit: string; reference_date: string; checked_at: string; source: string; stale: boolean };
type SimKind = 'fixed' | 'variable' | 'foreign';

/** Calculadora (SPEC-013/004), simulações (SPEC-008/009/026), comparação (SPEC-010) e indicadores (SPEC-007). */
export function Investments({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [projection, setProjection] = useState<Projection | null>(null);
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [indicators, setIndicators] = useState<Record<string, Indicator | null>>({});
  const [simKind, setSimKind] = useState<SimKind>('fixed');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try { setSimulations(await api<Simulation[]>(token, '/financial/simulations')); }
    catch (cause) { setError(errorText(cause, lang)); }
  }, [token, lang]);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    for (const code of ['selic', 'cdi', 'ipca']) {
      void api<Indicator>(token, `/financial/indicators/${code}`)
        .then(value => setIndicators(current => ({ ...current, [code]: value })))
        .catch(() => setIndicators(current => ({ ...current, [code]: null })));
    }
  }, [token]);

  async function calculate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const product = String(data.get('calc-product'));
    const body = { initial_amount: data.get('calc-initial'), monthly_contribution: data.get('calc-monthly'), annual_rate: data.get('calc-rate'), term_months: Number(data.get('calc-term')) };
    setError('');
    try {
      setProjection(await api<Projection>(token, product === 'none' ? '/financial/calculator' : '/financial/fixed-income-projections', {
        method: 'POST', body: JSON.stringify(product === 'none' ? body : { ...body, product }),
      }));
    } catch (cause) { setError(errorText(cause, lang)); }
  }

  async function saveSimulation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget; const data = Object.fromEntries(new FormData(form)) as Record<string, string>;
    const common = { label: data.label, initial_amount: data.initial, monthly_contribution: data.monthly, term_months: Number(data.term) };
    const [path, body] = simKind === 'fixed'
      ? ['/financial/simulations/fixed-income', { ...common, annual_rate: data.rate, product: data.product }]
      : simKind === 'variable'
        ? ['/financial/simulations/variable-income', { ...common, expected_annual_return: data.rate, ticker: data.ticker || null }]
        : ['/financial/simulations/foreign-currency', { ...common, asset_annual_return: data.rate, currency: data.currency, expected_exchange_annual_change: data.exchange }];
    setError(''); setStatus('');
    try { await api(token, path, { method: 'POST', body: JSON.stringify(body) }); form.reset(); setStatus(pt ? 'Simulação salva.' : 'Simulation saved.'); await load(); }
    catch (cause) { setError(errorText(cause, lang)); }
  }

  async function compare() {
    setError('');
    try { setComparison(await api<Comparison>(token, '/financial/simulations/compare', { method: 'POST', body: JSON.stringify({ simulation_ids: selected }) })); }
    catch (cause) { setError(errorText(cause, lang)); }
  }

  const kindLabel = (kind: string) => ({ fixed_income: pt ? 'Renda fixa' : 'Fixed income', variable_income: pt ? 'Renda variável' : 'Variable income', foreign_currency: pt ? 'Moeda estrangeira' : 'Foreign currency' }[kind] ?? kind);
  const series = projection?.monthly_series ?? [];
  const peak = Math.max(1, ...series.map(row => Number(row.closing_balance)));
  const step = Math.max(1, Math.ceil(series.length / 24));
  const sampled = series.filter((_, index) => index % step === 0 || index === series.length - 1);

  return <div className="stack">
    {error && <p className="error" role="alert">{error}</p>}
    <section className="profile" aria-labelledby="indicators-title">
      <h3 id="indicators-title">{pt ? 'Indicadores oficiais' : 'Official indicators'}</h3>
      <div className="kpis">{['selic', 'cdi', 'ipca'].map(code => {
        const item = indicators[code];
        return <div className="kpi" key={code}><span>{code.toUpperCase()}</span>
          {item ? <><strong>{percent(item.value, lang)}</strong><small>{pt ? 'Ref.' : 'Ref.'} {shortDate(item.reference_date, lang)} · {item.source}{item.stale ? (pt ? ' · desatualizado' : ' · stale') : ''}</small></>
            : <small>{item === null ? (pt ? 'Indisponível no cache local' : 'Unavailable in local cache') : (pt ? 'Carregando…' : 'Loading…')}</small>}
        </div>;
      })}</div>
    </section>

    <div className="grid-2">
      <section className="profile" aria-labelledby="calculator-title">
        <h3 id="calculator-title">{pt ? 'Calculadora de juros compostos' : 'Compound interest calculator'}</h3>
        <form onSubmit={calculate}>
          <div className="field"><label htmlFor="calc-initial">{pt ? 'Valor inicial (R$)' : 'Initial amount (BRL)'}</label><input id="calc-initial" name="calc-initial" type="number" min="0" step="0.01" defaultValue="1000" required /></div>
          <div className="field"><label htmlFor="calc-monthly">{pt ? 'Aporte mensal (R$)' : 'Monthly contribution (BRL)'}</label><input id="calc-monthly" name="calc-monthly" type="number" min="0" step="0.01" defaultValue="200" required /></div>
          <div className="field"><label htmlFor="calc-rate">{pt ? 'Taxa anual (%)' : 'Annual rate (%)'}</label><input id="calc-rate" name="calc-rate" type="number" min="0" step="0.01" defaultValue="10" required /></div>
          <div className="field"><label htmlFor="calc-term">{pt ? 'Prazo (meses)' : 'Term (months)'}</label><input id="calc-term" name="calc-term" type="number" min="1" max="720" defaultValue="24" required /></div>
          <div className="field"><label htmlFor="calc-product">{pt ? 'Imposto de renda' : 'Income tax'}</label>
            <select id="calc-product" name="calc-product" defaultValue="none"><option value="none">{pt ? 'Sem IR (valor bruto)' : 'No tax (gross)'}</option><option value="cdb">CDB</option><option value="tesouro">Tesouro Direto</option><option value="poupanca">{pt ? 'Poupança (isenta)' : 'Savings (exempt)'}</option></select></div>
          <button type="submit">{pt ? 'Calcular' : 'Calculate'}</button>
        </form>
      </section>
      <section className="profile" aria-labelledby="calc-result-title">
        <h3 id="calc-result-title">{pt ? 'Resultado' : 'Result'}</h3>
        {!projection ? <p>{pt ? 'Preencha a calculadora para ver a projeção.' : 'Fill in the calculator to see the projection.'}</p> : <>
          <div className="kpis">
            <div className="kpi"><span>{pt ? 'Total investido' : 'Invested'}</span><strong>{money(projection.invested, lang)}</strong></div>
            <div className="kpi"><span>{pt ? 'Juros' : 'Interest'}</span><strong className="positive">{money(projection.interest, lang)}</strong></div>
            <div className="kpi"><span>{pt ? 'Montante bruto' : 'Gross amount'}</span><strong>{money(projection.gross_amount, lang)}</strong></div>
            {projection.net_amount && <div className="kpi"><span>{pt ? 'Líquido' : 'Net'} ({pt ? 'IR' : 'tax'} {percent(projection.tax_rate ?? 0, lang, 1)})</span><strong>{money(projection.net_amount, lang)}</strong></div>}
          </div>
          <svg viewBox="0 0 360 150" className="chart" role="img" aria-label={pt ? 'Evolução do saldo mês a mês' : 'Monthly balance evolution'}>
            {sampled.map((row, index) => {
              const width = 340 / sampled.length; const height = Number(row.closing_balance) / peak * 120;
              return <rect key={row.month} x={10 + index * width} y={130 - height} width={Math.max(2, width - 3)} height={height} rx="2" className="bar-income"><title>{pt ? 'Mês' : 'Month'} {row.month}: {money(row.closing_balance, lang)}</title></rect>;
            })}
          </svg>
          <p className="hint">{projection.rate_explanation}</p>
          {projection.investor_guidance && <p className="hint">{projection.investor_guidance}</p>}
        </>}
      </section>
    </div>

    <section className="profile" aria-labelledby="simulate-title">
      <h3 id="simulate-title">{pt ? 'Salvar simulação' : 'Save a simulation'}</h3>
      <div className="segmented" role="group" aria-label={pt ? 'Tipo de simulação' : 'Simulation type'}>
        {([['fixed', pt ? 'Renda fixa' : 'Fixed income'], ['variable', pt ? 'Renda variável' : 'Variable income'], ['foreign', pt ? 'Moeda estrangeira' : 'Foreign currency']] as [SimKind, string][])
          .map(([value, label]) => <button key={value} type="button" aria-pressed={simKind === value} onClick={() => setSimKind(value)}>{label}</button>)}
      </div>
      <form onSubmit={saveSimulation} className="form-grid" key={simKind}>
        <div className="field"><label htmlFor="sim-label">{pt ? 'Nome da simulação' : 'Simulation name'}</label><input id="sim-label" name="label" maxLength={100} required /></div>
        <div className="field"><label htmlFor="sim-initial">{pt ? 'Valor inicial (R$)' : 'Initial amount (BRL)'}</label><input id="sim-initial" name="initial" type="number" min="0" step="0.01" defaultValue="1000" required /></div>
        <div className="field"><label htmlFor="sim-monthly">{pt ? 'Aporte mensal (R$)' : 'Monthly contribution (BRL)'}</label><input id="sim-monthly" name="monthly" type="number" min="0" step="0.01" defaultValue="200" required /></div>
        <div className="field"><label htmlFor="sim-rate">{simKind === 'fixed' ? (pt ? 'Taxa anual (%)' : 'Annual rate (%)') : (pt ? 'Retorno anual esperado (%)' : 'Expected annual return (%)')}</label><input id="sim-rate" name="rate" type="number" min="0" step="0.01" defaultValue="10" required /></div>
        <div className="field"><label htmlFor="sim-term">{pt ? 'Prazo (meses)' : 'Term (months)'}</label><input id="sim-term" name="term" type="number" min="1" max="720" defaultValue="24" required /></div>
        {simKind === 'fixed' && <div className="field"><label htmlFor="sim-product">{pt ? 'Produto' : 'Product'}</label><select id="sim-product" name="product"><option value="cdb">CDB</option><option value="tesouro">Tesouro Direto</option><option value="poupanca">{pt ? 'Poupança' : 'Savings'}</option></select></div>}
        {simKind === 'variable' && <div className="field"><label htmlFor="sim-ticker">{pt ? 'Ticker de referência (opcional)' : 'Reference ticker (optional)'}</label><input id="sim-ticker" name="ticker" pattern="[A-Za-z]{4,5}[0-9]{1,2}" placeholder="PETR4" /></div>}
        {simKind === 'foreign' && <div className="field"><label htmlFor="sim-currency">{pt ? 'Moeda' : 'Currency'}</label><select id="sim-currency" name="currency"><option value="USD">USD</option><option value="EUR">EUR</option></select></div>}
        {simKind === 'foreign' && <div className="field"><label htmlFor="sim-exchange">{pt ? 'Variação cambial anual esperada (%)' : 'Expected annual FX change (%)'}</label><input id="sim-exchange" name="exchange" type="number" step="0.01" defaultValue="3" required /></div>}
        <div className="actions"><button type="submit">{pt ? 'Simular e salvar' : 'Simulate and save'}</button></div>
      </form>
      <p className="message" role="status" aria-live="polite">{status}</p>
    </section>

    <section className="profile" aria-labelledby="simulations-title">
      <h3 id="simulations-title">{pt ? 'Minhas simulações' : 'My simulations'}</h3>
      <p className="hint">{pt ? 'Simulações não alteram seu saldo nem seu patrimônio real. Selecione de 2 a 10 para comparar.' : 'Simulations never change your real balance. Select 2 to 10 to compare.'}</p>
      {simulations.length === 0 ? <p>{pt ? 'Nenhuma simulação salva.' : 'No saved simulations.'}</p> : <>
        <div className="table-wrap" tabIndex={0}><table>
          <caption>{pt ? 'Simulações salvas' : 'Saved simulations'}</caption>
          <thead><tr><th><span className="sr-only">{pt ? 'Selecionar' : 'Select'}</span></th><th>{pt ? 'Nome' : 'Name'}</th><th>{pt ? 'Tipo' : 'Type'}</th><th>{pt ? 'Criada em' : 'Created'}</th><th className="num">{pt ? 'Valor final' : 'Final amount'}</th></tr></thead>
          <tbody>{simulations.map(item => <tr key={item.id}>
            <td><input type="checkbox" aria-label={`${pt ? 'Selecionar' : 'Select'} ${item.label}`} checked={selected.includes(item.id)} onChange={event => setSelected(current => event.target.checked ? [...current, item.id].slice(-10) : current.filter(id => id !== item.id))} /></td>
            <td>{item.label}</td><td>{kindLabel(item.kind)}</td><td>{shortDate(item.created_at, lang)}</td><td className="num">{money(item.final_amount, lang)}</td>
          </tr>)}</tbody>
        </table></div>
        <button type="button" disabled={selected.length < 2} onClick={() => void compare()}>{pt ? 'Comparar selecionadas' : 'Compare selected'}</button>
      </>}
      {comparison && <div className="table-wrap" tabIndex={0}><table>
        <caption>{pt ? 'Comparação: diferença em relação à primeira simulação' : 'Comparison: difference from the first simulation'}</caption>
        <thead><tr><th>{pt ? 'Simulação' : 'Simulation'}</th><th className="num">{pt ? 'Valor final' : 'Final amount'}</th><th className="num">{pt ? 'Diferença' : 'Difference'}</th></tr></thead>
        <tbody>{comparison.simulations.map((item, index) => <tr key={item.id}><td>{item.label}</td><td className="num">{money(item.final_amount, lang)}</td><td className="num">{money(comparison.difference_from_first[index], lang)}</td></tr>)}</tbody>
      </table></div>}
    </section>
  </div>;
}
