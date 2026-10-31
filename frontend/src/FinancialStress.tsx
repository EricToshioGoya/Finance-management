import { useState, type FormEvent } from 'react';

type Kind = 'income_loss' | 'income_reduction' | 'emergency_expense';
type Scenario = {
  kind: Kind; months: number; reduction_percent: number;
  emergency_amount: number; expense_cut_percent: number;
};
type Result = {
  months_supported: string | null;
  remaining_reserve: string;
  reserve_months_before_shock: string;
  low_reserve: boolean;
  falls_below_threshold: boolean;
  horizon_reached: boolean;
};
type Comparison = {
  reserve: string; real_net_worth: string;
  average_monthly_income: string; average_monthly_expenses: string;
  window_months: number; rule_version: string;
  first: Result; second: Result;
};
const defaultScenario = (): Scenario => ({
  kind: 'income_loss', months: 6, reduction_percent: 0,
  emergency_amount: 0, expense_cut_percent: 0,
});
const currency = (value: string, lang: 'pt' | 'en') =>
  new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency: 'BRL',
  }).format(Number(value));

export function FinancialStress({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [first, setFirst] = useState<Scenario>(defaultScenario);
  const [second, setSecond] = useState<Scenario>({
    ...defaultScenario(), expense_cut_percent: 30,
  });
  const [threshold, setThreshold] = useState(3);
  const [result, setResult] = useState<Comparison | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function compare(event: FormEvent) {
    event.preventDefault();
    setBusy(true); setError(''); setResult(null);
    try {
      const response = await fetch('/api/v1/auth/financial/stress/compare', {
        method: 'POST',
        headers: {
          Authorization: 'Bearer ' + token,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          minimum_reserve_months: threshold,
          first, second,
        }),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({})) as { detail?: string };
        throw new Error(body.detail === 'stress_expense_history_required'
          ? 'no-expenses' : 'request');
      }
      setResult(await response.json() as Comparison);
    } catch (exc) {
      setError(exc instanceof Error && exc.message === 'no-expenses'
        ? pt ? 'Cadastre despesas reais nos últimos três meses completos antes de simular.' :
          'Add actual expenses in the previous three complete months before simulating.'
        : pt ? 'Não foi possível calcular. Revise os parâmetros e tente novamente.' :
          'Calculation unavailable. Check the parameters and retry.');
    } finally { setBusy(false); }
  }

  function fields(
    title: string, value: Scenario,
    change: (scenario: Scenario) => void,
  ) {
    return <fieldset style={{ flex: '1 1 240px', minWidth: 0 }} disabled={busy}>
      <legend>{title}</legend>
      <label>{pt ? 'Choque' : 'Shock'}
        <select value={value.kind} onChange={event =>
          change({ ...value, kind: event.target.value as Kind,
            reduction_percent: 0, emergency_amount: 0 })}>
          <option value="income_loss">{pt ? 'Perda total da renda' : 'Total loss of income'}</option>
          <option value="income_reduction">{pt ? 'Redução de renda' : 'Income reduction'}</option>
          <option value="emergency_expense">{pt ? 'Gasto emergencial' : 'Emergency expense'}</option>
        </select>
      </label>
      <label>{pt ? 'Duração (meses)' : 'Duration (months)'}
        <input type="number" required min="1" max="120" step="1" value={value.months}
          onChange={event => change({ ...value, months: Number(event.target.value) })} />
      </label>
      {value.kind === 'income_reduction' && <label>
        {pt ? 'Redução de renda (%)' : 'Income reduction (%)'}
        <input type="number" required min="0.01" max="100" step="0.01"
          value={value.reduction_percent} onChange={event =>
            change({ ...value, reduction_percent: Number(event.target.value) })} />
      </label>}
      {value.kind === 'emergency_expense' && <label>
        {pt ? 'Despesa extraordinária (R$)' : 'One-time expense (BRL)'}
        <input type="number" required min="0.01" max="999999999" step="0.01"
          value={value.emergency_amount} onChange={event =>
            change({ ...value, emergency_amount: Number(event.target.value) })} />
      </label>}
      <label>{pt ? 'Redução hipotética dos gastos (%)' : 'Hypothetical spending cut (%)'}
        <input type="number" min="0" max="100" step="0.01"
          value={value.expense_cut_percent} onChange={event =>
            change({ ...value, expense_cut_percent: Number(event.target.value) })} />
      </label>
    </fieldset>;
  }

  const outcome = (label: string, row: Result) =>
    <section aria-label={label} style={{ flex: '1 1 240px' }}>
      <h4>{label}</h4>
      <p><strong>{pt ? 'Sustentação:' : 'Runway:'}</strong> {row.months_supported === null
        ? pt ? 'Não esgotada em 120 meses de projeção' : 'Not exhausted within 120 months'
        : row.months_supported + (pt ? ' meses' : ' months')}</p>
      <p>{pt ? 'Reserva ao final da projeção:' : 'Reserve at projection end:'}
        {' '}{currency(row.remaining_reserve, lang)}</p>
      {row.falls_below_threshold && <p role="status">
        {pt ? 'Alerta: reserva insuficiente para o limite escolhido neste cenário.' :
          'Warning: reserve falls below the selected runway threshold.'}
      </p>}
      {row.low_reserve && <p role="status">
        {pt ? 'Reserva inicial inferior ao limite de segurança.' :
          'Starting reserve is below the safety threshold.'}
      </p>}
    </section>;

  return <section className="profile" aria-labelledby="stress-title">
    <h3 id="stress-title">{pt ? 'Simulador de stress financeiro' : 'Financial stress simulator'}</h3>
    <p>{pt ? 'Compare dois choques hipotéticos sem modificar seus saldos ou registros.' :
      'Compare two hypothetical shocks without changing your balances or records.'}</p>
    <form onSubmit={event => void compare(event)} aria-busy={busy}>
      <label>{pt ? 'Reserva mínima (meses)' : 'Minimum reserve (months)'}
        <select value={threshold} onChange={event => setThreshold(Number(event.target.value))}>
          {[3, 4, 5, 6].map(months => <option key={months} value={months}>{months}</option>)}
        </select>
      </label>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
        {fields(pt ? 'Cenário A' : 'Scenario A', first, setFirst)}
        {fields(pt ? 'Cenário B' : 'Scenario B', second, setSecond)}
      </div>
      <button disabled={busy} type="submit">{pt ? 'Comparar cenários' : 'Compare scenarios'}</button>
    </form>
    {error && <p role="alert">{error}</p>}
    {result && <div aria-live="polite">
      <p>{pt ? 'Patrimônio líquido real:' : 'Real net worth:'}
        {' '}{currency(result.real_net_worth, lang)}.{' '}
        {pt ? 'Reserva conservadora:' : 'Conservative reserve:'}
        {' '}{currency(result.reserve, lang)}.</p>
      <p>{pt ? 'Médias de três meses completos — renda:' : 'Three complete months average — income:'}
        {' '}{currency(result.average_monthly_income, lang)};{' '}
        {pt ? 'gastos:' : 'expenses:'}
        {' '}{currency(result.average_monthly_expenses, lang)}.</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
        {outcome(pt ? 'Cenário A' : 'Scenario A', result.first)}
        {outcome(pt ? 'Cenário B' : 'Scenario B', result.second)}
      </div>
    </div>}
    <small>{pt
      ? 'Regra stress-v1: reserva = saldos não negativos de contas correntes, poupança e dinheiro, sem ativos de liquidez desconhecida. Gasto e renda médios dos três meses anteriores completos; choque limitado à duração informada. Projeção máxima de 120 meses, sem juros, inflação ou novos investimentos; não é previsão nem recomendação.'
      : 'stress-v1: reserve includes checking, savings and cash only, excluding assets with unknown liquidity. Income and expenses use the prior three complete months. Shocks are limited to their duration. Maximum 120-month projection, without interest, inflation or new investments. Not a forecast or advice.'}</small>
  </section>;
}
