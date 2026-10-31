import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, currentCompetence, errorText, money, percent, shortDate, type Lang } from './api';

type Retirement = { months: number; invested: string; projected_wealth: string; estimated_monthly_income: string; withdrawal_rate: string; suggested_rate: { code: string; value: string; stale: boolean } | null; assumptions: string[]; notice: string };
type Pension = { regime: string; rule_version: string; results: { modality: 'pgbl' | 'vgbl' | 'own_portfolio'; invested: string; gross_amount: string; earnings: string; tax: string; net_amount: string; effective_tax_rate: string }[]; pgbl_context: string; notice: string };
type Estimate = { id: string; regime: string; competence: string; sales: string; result: string; tax_rate: string; tax: string; exempt: boolean; darf_due_on: string | null; rule_version: string; notes: string[]; notice: string };
type Annual = { year: number; registered_income: { recurring_income: string; one_time_income: string; bonus: string; total: string }; tax_estimates: Estimate[]; estimated_tax_total: string; simulations: { label: string; kind: string; final_amount: string; origin: string }[]; notice: string };

/** Aposentadoria e renda estimada (SPEC-046). */
export function RetirementPlanner({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [result, setResult] = useState<Retirement | null>(null);
  const [error, setError] = useState('');
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setError('');
    try {
      setResult(await api<Retirement>(token, '/financial/retirement-projections', { method: 'POST', body: JSON.stringify({
        current_age: Number(data.get('ret-age')), target_age: Number(data.get('ret-target')), initial_amount: data.get('ret-initial') || '0',
        monthly_contribution: data.get('ret-monthly'), annual_rate: data.get('ret-rate'), withdrawal_rate: data.get('ret-withdrawal') || '4',
      }) }));
    } catch (cause) {
      setResult(null);
      setError(cause instanceof Error && cause.message === 'idade_alvo_deve_ser_futura' ? (pt ? 'A idade de aposentadoria precisa ser maior que a idade atual.' : 'Retirement age must be greater than current age.') : errorText(cause, lang));
    }
  }
  return <section className="profile" aria-labelledby="retirement-title">
    <h3 id="retirement-title">{pt ? 'Aposentadoria' : 'Retirement'}</h3>
    <form onSubmit={submit} className="form-grid">
      <div className="field"><label htmlFor="ret-age">{pt ? 'Idade atual' : 'Current age'}</label><input id="ret-age" name="ret-age" type="number" min="14" max="100" defaultValue="25" required /></div>
      <div className="field"><label htmlFor="ret-target">{pt ? 'Idade para se aposentar' : 'Retirement age'}</label><input id="ret-target" name="ret-target" type="number" min="15" max="110" defaultValue="60" required /></div>
      <div className="field"><label htmlFor="ret-initial">{pt ? 'Valor já guardado (R$)' : 'Current savings (BRL)'}</label><input id="ret-initial" name="ret-initial" type="number" min="0" step="0.01" defaultValue="0" /></div>
      <div className="field"><label htmlFor="ret-monthly">{pt ? 'Aporte mensal (R$)' : 'Monthly contribution (BRL)'}</label><input id="ret-monthly" name="ret-monthly" type="number" min="0" step="0.01" defaultValue="500" required /></div>
      <div className="field"><label htmlFor="ret-rate">{pt ? 'Rentabilidade anual (%)' : 'Annual return (%)'}</label><input id="ret-rate" name="ret-rate" type="number" min="0" max="100" step="0.01" defaultValue="8" required /></div>
      <div className="field"><label htmlFor="ret-withdrawal">{pt ? 'Taxa de retirada anual (%)' : 'Annual withdrawal rate (%)'}</label><input id="ret-withdrawal" name="ret-withdrawal" type="number" min="0.1" max="20" step="0.1" defaultValue="4" /></div>
      <div className="actions"><button type="submit">{pt ? 'Projetar' : 'Project'}</button></div>
    </form>
    {error && <p className="error" role="alert">{error}</p>}
    {result && <div className="result" role="status">
      <div className="kpis">
        <div className="kpi"><span>{pt ? 'Patrimônio projetado' : 'Projected wealth'}</span><strong>{money(result.projected_wealth, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Renda mensal estimada' : 'Estimated monthly income'}</span><strong className="positive">{money(result.estimated_monthly_income, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Total investido' : 'Invested'}</span><strong>{money(result.invested, lang)}</strong></div>
      </div>
      {result.suggested_rate && <p className="hint">{pt ? 'Referência atual' : 'Current reference'}: {result.suggested_rate.code.toUpperCase()} {percent(result.suggested_rate.value, lang)}{result.suggested_rate.stale ? (pt ? ' (desatualizada)' : ' (stale)') : ''}</p>}
      <ul className="hint">{result.assumptions.map(item => <li key={item}>{item}</li>)}</ul>
      <p className="hint"><strong>{result.notice}</strong></p>
    </div>}
  </section>;
}

/** PGBL x VGBL x carteira própria (SPEC-047). */
export function PensionComparison({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [regime, setRegime] = useState<'regressive' | 'progressive'>('regressive');
  const [result, setResult] = useState<Pension | null>(null);
  const [error, setError] = useState('');
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setError('');
    try {
      setResult(await api<Pension>(token, '/financial/pension-comparisons', { method: 'POST', body: JSON.stringify({
        initial_amount: data.get('pen-initial') || '0', monthly_contribution: data.get('pen-monthly'), annual_rate: data.get('pen-rate'),
        term_months: Number(data.get('pen-years')) * 12, regime, progressive_rate: regime === 'progressive' ? data.get('pen-progressive') : null,
      }) }));
    } catch (cause) { setResult(null); setError(errorText(cause, lang)); }
  }
  const names = { pgbl: 'PGBL', vgbl: 'VGBL', own_portfolio: pt ? 'Carteira própria' : 'Own portfolio' };
  return <section className="profile" aria-labelledby="pension-title">
    <h3 id="pension-title">{pt ? 'Previdência: PGBL x VGBL x carteira própria' : 'Pension: PGBL vs VGBL vs own portfolio'}</h3>
    <form onSubmit={submit} className="form-grid">
      <div className="field"><label htmlFor="pen-initial">{pt ? 'Valor inicial (R$)' : 'Initial amount (BRL)'}</label><input id="pen-initial" name="pen-initial" type="number" min="0" step="0.01" defaultValue="0" /></div>
      <div className="field"><label htmlFor="pen-monthly">{pt ? 'Aporte mensal (R$)' : 'Monthly contribution (BRL)'}</label><input id="pen-monthly" name="pen-monthly" type="number" min="0" step="0.01" defaultValue="500" required /></div>
      <div className="field"><label htmlFor="pen-rate">{pt ? 'Rentabilidade anual (%)' : 'Annual return (%)'}</label><input id="pen-rate" name="pen-rate" type="number" min="0" max="100" step="0.01" defaultValue="8" required /></div>
      <div className="field"><label htmlFor="pen-years">{pt ? 'Prazo (anos)' : 'Term (years)'}</label><input id="pen-years" name="pen-years" type="number" min="1" max="60" defaultValue="15" required /></div>
      <div className="field"><label htmlFor="pen-regime">{pt ? 'Regime de tributação' : 'Tax regime'}</label>
        <select id="pen-regime" value={regime} onChange={event => setRegime(event.target.value as 'regressive' | 'progressive')}><option value="regressive">{pt ? 'Regressivo' : 'Regressive'}</option><option value="progressive">{pt ? 'Progressivo' : 'Progressive'}</option></select></div>
      {regime === 'progressive' && <div className="field"><label htmlFor="pen-progressive">{pt ? 'Sua alíquota efetiva (%)' : 'Your effective rate (%)'}</label><input id="pen-progressive" name="pen-progressive" type="number" min="0" max="27.5" step="0.1" required /></div>}
      <div className="actions"><button type="submit">{pt ? 'Comparar' : 'Compare'}</button></div>
    </form>
    {error && <p className="error" role="alert">{error}</p>}
    {result && <>
      <div className="table-wrap" tabIndex={0}><table>
        <caption>{pt ? 'Valores líquidos com os mesmos parâmetros' : 'Net amounts with the same parameters'} · {pt ? 'tabela' : 'table'} {result.rule_version}</caption>
        <thead><tr><th>{pt ? 'Modalidade' : 'Option'}</th><th className="num">{pt ? 'Bruto' : 'Gross'}</th><th className="num">{pt ? 'Imposto' : 'Tax'}</th><th className="num">{pt ? 'Alíquota efetiva' : 'Effective rate'}</th><th className="num">{pt ? 'Líquido' : 'Net'}</th></tr></thead>
        <tbody>{result.results.map(item => <tr key={item.modality}><th scope="row">{names[item.modality]}</th><td className="num">{money(item.gross_amount, lang)}</td><td className="num negative">{money(item.tax, lang)}</td><td className="num">{percent(item.effective_tax_rate, lang)}</td><td className="num"><strong>{money(item.net_amount, lang)}</strong></td></tr>)}</tbody>
      </table></div>
      <p className="hint">{result.pgbl_context}</p>
      <p className="hint"><strong>{result.notice}</strong></p>
    </>}
  </section>;
}

/** Estimativa de IR e lembrete de DARF (SPEC-048) e resumo anual auxiliar (SPEC-049). */
export function Taxes({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [regime, setRegime] = useState('stock');
  const [estimates, setEstimates] = useState<Estimate[]>([]);
  const [last, setLast] = useState<Estimate | null>(null);
  const [year, setYear] = useState(Number(currentCompetence().slice(0, 4)));
  const [annual, setAnnual] = useState<Annual | null>(null);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    try { setEstimates(await api<Estimate[]>(token, '/financial/tax-estimates')); } catch (cause) { setError(errorText(cause, lang)); }
    try { setAnnual(await api<Annual>(token, `/financial/annual-summary?year=${year}`)); } catch { setAnnual(null); }
  }, [token, lang, year]);
  useEffect(() => { void load(); }, [load]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget; const data = new FormData(form);
    setError('');
    try {
      setLast(await api<Estimate>(token, '/financial/tax-estimates', { method: 'POST', body: JSON.stringify({
        regime, competence: data.get('tax-month'), result: data.get('tax-result'), sales: data.get('tax-sales') || '0',
        holding_days: regime === 'fixed_income' ? Number(data.get('tax-days')) : null,
      }) }));
      await load();
    } catch (cause) { setError(errorText(cause, lang)); }
  }
  async function download(format: 'csv' | 'pdf') {
    const response = await fetch(`/api/v1/auth/financial/annual-summary/${format}?year=${year}`, { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) { setError(pt ? 'Não há dados para o ano selecionado.' : 'No data for the selected year.'); return; }
    const url = URL.createObjectURL(await response.blob());
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `resumo-anual-${year}.${format}`; anchor.click(); URL.revokeObjectURL(url);
  }
  const regimeName = (value: string) => ({ stock: pt ? 'Ações (operação comum)' : 'Stocks (swing)', fii: 'FIIs', day_trade: 'Day trade', fixed_income: pt ? 'Renda fixa' : 'Fixed income' }[value] ?? value);
  return <div className="stack">
    {error && <p className="error" role="alert">{error}</p>}
    <div className="grid-2">
      <section className="profile" aria-labelledby="tax-title">
        <h3 id="tax-title">{pt ? 'Estimar imposto de renda' : 'Estimate income tax'}</h3>
        <form onSubmit={submit}>
          <div className="field"><label htmlFor="tax-regime">{pt ? 'Tipo de operação' : 'Operation type'}</label>
            <select id="tax-regime" value={regime} onChange={event => setRegime(event.target.value)}>{['stock', 'fii', 'day_trade', 'fixed_income'].map(value => <option key={value} value={value}>{regimeName(value)}</option>)}</select></div>
          <div className="inline-fields">
            <div className="field"><label htmlFor="tax-month">{pt ? 'Mês da operação' : 'Month of operation'}</label><input id="tax-month" name="tax-month" type="month" defaultValue={currentCompetence()} required /></div>
            <div className="field"><label htmlFor="tax-result">{pt ? 'Lucro ou prejuízo (R$)' : 'Profit or loss (BRL)'}</label><input id="tax-result" name="tax-result" type="number" step="0.01" required /></div>
          </div>
          {regime === 'stock' && <div className="field"><label htmlFor="tax-sales">{pt ? 'Total de vendas de ações no mês (R$)' : 'Total stock sales in the month (BRL)'}</label><input id="tax-sales" name="tax-sales" type="number" min="0" step="0.01" required /></div>}
          {regime === 'fixed_income' && <div className="field"><label htmlFor="tax-days">{pt ? 'Dias de aplicação' : 'Days invested'}</label><input id="tax-days" name="tax-days" type="number" min="1" required /></div>}
          <button type="submit">{pt ? 'Estimar' : 'Estimate'}</button>
        </form>
        {last && <div className="result" role="status">
          <p>{pt ? 'IR estimado' : 'Estimated tax'}: <strong>{money(last.tax, lang)}</strong> ({percent(last.tax_rate, lang, 1)}){last.exempt && (pt ? ' — isento' : ' — exempt')}</p>
          {last.darf_due_on && <p className="negative">{pt ? 'Pague o DARF até' : 'Pay the DARF by'} <strong>{shortDate(last.darf_due_on, lang)}</strong></p>}
          <ul className="hint">{last.notes.map(note => <li key={note}>{note}</li>)}</ul>
          <small>{last.notice}</small>
        </div>}
      </section>
      <section className="profile" aria-labelledby="tax-list-title">
        <h3 id="tax-list-title">{pt ? 'Estimativas registradas' : 'Saved estimates'}</h3>
        {estimates.length === 0 ? <p>{pt ? 'Nenhuma estimativa.' : 'No estimates.'}</p> : <div className="table-wrap" tabIndex={0}><table>
          <caption>{pt ? 'Estimativas de IR e vencimentos de DARF' : 'Tax estimates and DARF due dates'}</caption>
          <thead><tr><th>{pt ? 'Mês' : 'Month'}</th><th>{pt ? 'Tipo' : 'Type'}</th><th className="num">IR</th><th>DARF</th><th><span className="sr-only">{pt ? 'Ações' : 'Actions'}</span></th></tr></thead>
          <tbody>{estimates.map(item => <tr key={item.id}><td>{item.competence}</td><td>{regimeName(item.regime)}</td><td className="num">{money(item.tax, lang)}</td><td>{item.darf_due_on ? shortDate(item.darf_due_on, lang) : '—'}</td>
            <td className="row-actions"><button type="button" className="secondary danger" aria-label={`${pt ? 'Excluir estimativa' : 'Delete estimate'} ${item.competence}`} onClick={() => void api(token, `/financial/tax-estimates/${item.id}`, { method: 'DELETE' }).then(load)}>{pt ? 'Excluir' : 'Delete'}</button></td></tr>)}</tbody>
        </table></div>}
      </section>
    </div>
    <section className="profile" aria-labelledby="annual-title">
      <div className="section-heading"><h3 id="annual-title">{pt ? 'Resumo anual auxiliar' : 'Annual summary'}</h3>
        <label className="inline-field">{pt ? 'Ano' : 'Year'}<input type="number" min="2000" max="2100" value={year} onChange={event => setYear(Number(event.target.value))} /></label></div>
      {!annual ? <p>{pt ? 'Sem dados registrados ou simulados neste ano.' : 'No recorded or simulated data for this year.'}</p> : <>
        <div className="kpis">
          <div className="kpi"><span>{pt ? 'Rendimentos registrados' : 'Recorded income'}</span><strong>{money(annual.registered_income.total, lang)}</strong></div>
          <div className="kpi"><span>{pt ? 'IR estimado no ano' : 'Estimated tax'}</span><strong>{money(annual.estimated_tax_total, lang)}</strong></div>
          <div className="kpi"><span>{pt ? 'Simulações do ano' : 'Simulations'}</span><strong>{annual.simulations.length}</strong></div>
        </div>
        <p className="hint"><strong>{annual.notice}</strong></p>
        <div className="actions"><button type="button" onClick={() => void download('csv')}>{pt ? 'Baixar CSV' : 'Download CSV'}</button><button type="button" className="secondary" onClick={() => void download('pdf')}>{pt ? 'Baixar PDF' : 'Download PDF'}</button></div>
      </>}
    </section>
  </div>;
}
