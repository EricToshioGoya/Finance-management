import { useState, type FormEvent } from 'react';
import { ContextualHelp } from './Education';

type Comparison = {
  asset_value: string; down_payment: string;
  financing_months: number; comparison_horizon_months: number;
  financing_annual_rate: string; investment_annual_rate: string;
  monthly_investment: string; financing_total_paid: string;
  financing_total_interest: string; financing_possession_month: number;
  invest_possession_month: number | null; invested_by_horizon: string;
  investment_balance_at_horizon: string; invest_cost_to_possession: string | null;
  invest_balance_at_possession: string | null; nominal_purchase_price: string;
  nominal_cost_difference: string | null;
  lower_nominal_cost: 'finance_now' | 'invest_then_buy' | 'tie' | 'not_comparable';
  assumptions: string[];
};
const money = (value: string, lang: 'pt' | 'en') =>
  new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency: 'BRL',
  }).format(Number(value));

export function FinancingComparison({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [asset, setAsset] = useState('120000');
  const [down, setDown] = useState('20000');
  const [months, setMonths] = useState('120');
  const [horizon, setHorizon] = useState('120');
  const [financeRate, setFinanceRate] = useState('12');
  const [investRate, setInvestRate] = useState('8');
  const [result, setResult] = useState<Comparison | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function calculate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setError(''); setResult(null);
    try {
      const response = await fetch('/api/v1/auth/financial/financing/compare', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          asset_value: asset, down_payment: down, installments: Number(months),
          financing_annual_rate: financeRate, investment_annual_rate: investRate,
          horizon_months: Number(horizon),
        }),
      });
      if (!response.ok) throw new Error('invalid');
      setResult(await response.json() as Comparison);
    } catch {
      setError(pt ? 'Não foi possível comparar. Revise valores, taxas e prazos.' :
        'Could not compare. Check amounts, rates and time periods.');
    } finally { setBusy(false); }
  }

  const cheaper = result?.lower_nominal_cost;
  const costMessage = cheaper === 'not_comparable'
    ? (pt ? 'O alvo não foi alcançado no horizonte. Não há comparação de custo de compra concluída.' :
      'The target was not reached within the horizon. There is no completed purchase cost comparison.')
    : cheaper === 'tie'
      ? (pt ? 'Empate no custo nominal da compra, com datas de posse diferentes.' :
        'The nominal purchase cost is tied, but possession times differ.')
      : cheaper === 'invest_then_buy'
        ? (pt ? 'Comprar à vista após investir tem menor preço nominal de aquisição, mas adia a posse.' :
          'Buying cash after investing has a lower nominal acquisition price, but delays possession.')
        : (pt ? 'Financiar agora tem menor custo nominal de aquisição neste modelo.' :
          'Financing now has a lower nominal acquisition cost in this model.');

  return <section className="profile" aria-labelledby="financing-compare-heading">
    <h3 id="financing-compare-heading">
      {pt ? 'Financiar agora ou investir antes?' : 'Finance now or invest first?'}
    </h3>
    <p>{pt
      ? 'Compare a posse imediata pelo financiamento Price com a compra à vista após investir a mesma entrada e o valor mensal da prestação.'
      : 'Compare immediate possession via Price financing with a later cash purchase by investing the same down payment and monthly installment.'}</p>
    <form onSubmit={event => void calculate(event)} aria-busy={busy}>
      <fieldset disabled={busy}>
        <legend>{pt ? 'Parâmetros dos cenários' : 'Scenario parameters'}</legend>
        <label>{pt ? 'Preço fixo do bem (R$)' : 'Fixed asset price (BRL)'}
          <input required type="number" min="0.01" step="0.01" value={asset}
            onChange={event => setAsset(event.target.value)} />
        </label>
        <label>{pt ? 'Entrada disponível (R$)' : 'Available down payment (BRL)'}
          <input required type="number" min="0" step="0.01" value={down}
            onChange={event => setDown(event.target.value)} />
        </label>
        <label>{pt ? 'Parcelas do financiamento' : 'Financing installments'}
          <input required type="number" min="1" max="600" step="1" value={months}
            onChange={event => setMonths(event.target.value)} />
        </label>
        <label>{pt ? 'Taxa efetiva anual do financiamento (%)' : 'Financing effective annual rate (%)'}
          <ContextualHelp token={token} lang={lang} articleKey="interest-rate" />
          <input required type="number" min="0" max="100" step="0.000001"
            value={financeRate} onChange={event => setFinanceRate(event.target.value)} />
        </label>
        <label>{pt ? 'Taxa anual hipotética do investimento (%)' : 'Hypothetical investment annual rate (%)'}
          <input required type="number" min="0" max="100" step="0.000001"
            value={investRate} onChange={event => setInvestRate(event.target.value)} />
        </label>
        <label>{pt ? 'Horizonte de comparação (meses)' : 'Comparison horizon (months)'}
          <input required type="number" min="1" max="600" step="1" value={horizon}
            onChange={event => setHorizon(event.target.value)} />
        </label>
      </fieldset>
      <button type="submit" disabled={busy}>
        {pt ? 'Comparar cenários' : 'Compare scenarios'}
      </button>
    </form>
    {error && <p role="alert">{error}</p>}
    {result && <div aria-live="polite">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
        gap: 16, marginBlock: 16 }}>
        <article>
          <h4>{pt ? 'Financiar agora' : 'Finance now'}</h4>
          <p>{pt ? 'Posse' : 'Possession'}: {pt ? 'imediata (mês 0)' : 'immediate (month 0)'}</p>
          <p>{pt ? 'Entrada' : 'Down payment'}: {money(result.down_payment, lang)}</p>
          <p>{pt ? 'Prestação usada na comparação' : 'Installment used in comparison'}:
            {' '}{money(result.monthly_investment, lang)}</p>
          <p>{pt ? 'Juros totais' : 'Total interest'}:
            {' '}{money(result.financing_total_interest, lang)}</p>
          <p><strong>{pt ? 'Total nominal pago' : 'Total nominal paid'}:
            {' '}{money(result.financing_total_paid, lang)}</strong></p>
          <p>{result.financing_months} {pt ? 'meses de financiamento' : 'financing months'}</p>
        </article>
        <article>
          <h4>{pt ? 'Investir e comprar à vista' : 'Invest then buy cash'}</h4>
          <p>{pt ? 'Aporte mensal' : 'Monthly contribution'}:
            {' '}{money(result.monthly_investment, lang)}</p>
          <p>{pt ? 'Posse' : 'Possession'}:
            {' '}{result.invest_possession_month === null
              ? (pt ? 'não alcançada no horizonte' : 'not reached within horizon')
              : (pt ? 'mês ' : 'month ') + result.invest_possession_month}</p>
          <p>{pt ? 'Preço à vista fixo' : 'Fixed cash price'}:
            {' '}{money(result.nominal_purchase_price, lang)}</p>
          <p>{pt ? 'Saldo projetado no horizonte' : 'Projected balance at horizon'}:
            {' '}{money(result.investment_balance_at_horizon, lang)}</p>
          <p>{pt ? 'Aportes até o horizonte' : 'Contributions through horizon'}:
            {' '}{money(result.invested_by_horizon, lang)}</p>
          {result.invest_cost_to_possession !== null && <p>
            {pt ? 'Capital aportado até atingir o preço' : 'Contributions until target'}:
            {' '}{money(result.invest_cost_to_possession, lang)}</p>}
        </article>
      </div>
      <p role="status"><strong>{costMessage}</strong></p>
      {result.nominal_cost_difference !== null && <p>
        {pt ? 'Diferença nominal entre total financiado e preço à vista' :
          'Nominal difference between financed total and cash price'}:
        {' '}{money(result.nominal_cost_difference, lang)}</p>}
      <small>{pt
        ? 'Hipóteses: preço do bem constante; entrada investida inicialmente, prestações equivalentes investidas ao fim de cada mês; juros compostos; sem IOF, CET, impostos, taxas, risco de investimento ou valorização do bem. O menor preço nominal não significa melhor decisão considerando tempo de posse, risco ou inflação. Simulação sem registro financeiro.'
        : 'Assumptions: fixed asset price; down payment invested at start and installment-sized contributions at month-end; compound interest; excludes taxes, lending fees, investment risk, asset appreciation and inflation. A lower nominal purchase price does not establish a better decision after considering possession timing, risk or inflation. No financial records created.'}</small>
    </div>}
  </section>;
}
