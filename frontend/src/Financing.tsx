import { useState, type FormEvent } from 'react';
import { ContextualHelp } from './Education';

type Installment = {
  number: number; payment: string; interest: string;
  principal: string; remaining_balance: string;
};
type Plan = {
  asset_value: string; down_payment: string; financed_amount: string;
  installments: number; annual_rate: string; monthly_rate: string;
  installment_amount: string; total_installments: string;
  total_paid: string; total_interest: string; schedule: Installment[];
  amortization_system: 'price'; simulated_only: boolean;
};
const money = (amount: string, lang: 'pt' | 'en') =>
  new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency: 'BRL',
  }).format(Number(amount));

export function Financing({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [value, setValue] = useState('120000');
  const [down, setDown] = useState('20000');
  const [months, setMonths] = useState('120');
  const [rate, setRate] = useState('12');
  const [plan, setPlan] = useState<Plan | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [showAll, setShowAll] = useState(false);

  async function calculate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setPlan(null); setError(''); setShowAll(false);
    try {
      const response = await fetch('/api/v1/auth/financial/financing/simulate', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          asset_value: value, down_payment: down,
          installments: Number(months), annual_rate: rate,
        }),
      });
      if (!response.ok) throw new Error('finance');
      setPlan(await response.json() as Plan);
    } catch {
      setError(pt ? 'Parâmetros inválidos ou simulação indisponível. Confira os valores.' :
        'Invalid parameters or unavailable calculation. Please check the values.');
    } finally { setBusy(false); }
  }

  return <section className="profile" aria-labelledby="financing-title">
    <h3 id="financing-title">{pt ? 'Simular compra financiada' : 'Financed purchase simulator'}</h3>
    <p>{pt ? 'Simulação educativa pela tabela Price, sem criar dívidas ou despesas reais.' :
      'Educational Price amortization simulation. No real debts or expenses are created.'}</p>
    <form onSubmit={event => void calculate(event)} aria-busy={busy}>
      <fieldset disabled={busy}>
        <legend>{pt ? 'Parâmetros da compra' : 'Purchase parameters'}</legend>
        <label>{pt ? 'Valor do bem (R$)' : 'Asset value (BRL)'}
          <input type="number" value={value} onChange={event => setValue(event.target.value)}
            required min="0.01" max="999999999999.99" step="0.01" />
        </label>
        <label>{pt ? 'Entrada (R$)' : 'Down payment (BRL)'}
          <input type="number" value={down} onChange={event => setDown(event.target.value)}
            required min="0" step="0.01" />
        </label>
        <label>{pt ? 'Parcelas (1 a 600)' : 'Installments (1 to 600)'}
          <input type="number" value={months} onChange={event => setMonths(event.target.value)}
            required min="1" max="600" step="1" />
        </label>
        <label>{pt ? 'Taxa efetiva anual (%)' : 'Effective annual interest (%)'}
          <ContextualHelp token={token} lang={lang} articleKey="interest-rate" />
          <input type="number" value={rate} onChange={event => setRate(event.target.value)}
            required min="0" max="100" step="0.000001" />
        </label>
      </fieldset>
      <button type="submit" disabled={busy}>{pt ? 'Calcular financiamento' : 'Calculate financing'}</button>
    </form>
    {error && <p role="alert">{error}</p>}
    {plan && <div aria-live="polite">
      <h4>{pt ? 'Resumo da simulação' : 'Simulation summary'}</h4>
      <p>{pt ? 'Valor financiado' : 'Financed principal'}: {money(plan.financed_amount, lang)}</p>
      <p>{pt ? 'Parcela de referência' : 'Reference installment'}: {money(plan.installment_amount, lang)}</p>
      <p>{pt ? 'Juros totais' : 'Total interest'}: {money(plan.total_interest, lang)}</p>
      <p>{pt ? 'Total das parcelas' : 'Installment total'}: {money(plan.total_installments, lang)}</p>
      <p><strong>{pt ? 'Total pago com entrada' : 'Total paid including down payment'}:
        {' '}{money(plan.total_paid, lang)}</strong></p>
      <h4>{pt ? 'Cronograma de amortização' : 'Amortization schedule'}</h4>
      <div className="indicator-table-wrap" style={{ overflowX: 'auto' }}>
        <table>
          <caption>{pt ? 'Tabela Price, valores mensais em reais' : 'Price schedule, monthly BRL amounts'}</caption>
          <thead><tr>
            <th scope="col">{pt ? 'Parcela' : 'No.'}</th>
            <th scope="col">{pt ? 'Pagamento' : 'Payment'}</th>
            <th scope="col">{pt ? 'Juros' : 'Interest'}</th>
            <th scope="col">{pt ? 'Amortização' : 'Principal'}</th>
            <th scope="col">{pt ? 'Saldo' : 'Balance'}</th>
          </tr></thead>
          <tbody>{(showAll ? plan.schedule : plan.schedule.slice(0, 24)).map(item => <tr key={item.number}>
            <th scope="row">{item.number}</th>
            <td>{money(item.payment, lang)}</td>
            <td>{money(item.interest, lang)}</td>
            <td>{money(item.principal, lang)}</td>
            <td>{money(item.remaining_balance, lang)}</td>
          </tr>)}</tbody>
        </table>
      </div>
      {plan.schedule.length > 24 && <button className="secondary" type="button"
        onClick={() => setShowAll(previous => !previous)}>
        {showAll ? pt ? 'Mostrar 24 parcelas' : 'Show 24 installments' :
          pt ? 'Mostrar todas as parcelas' : 'Show all installments'}
      </button>}
    </div>}
    <small>{pt
      ? 'Hipóteses: sistema Price com parcelas ao fim do mês, taxa anual convertida por equivalência composta. Sem IOF, seguro, tarifas, CET, correção monetária ou amortização antecipada; arredondamentos de exibição podem diferir de cobrança bancária. Nenhum financiamento real é registrado.'
      : 'Assumptions: Price system with end-of-month payments and equivalent monthly rate from an effective annual rate. No fees, insurance, taxes, effective total cost, indexing or early repayment. Display rounding may differ from lender billing. No real debt is recorded.'}</small>
  </section>;
}
