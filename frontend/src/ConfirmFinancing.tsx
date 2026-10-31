import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react';

type Debt = { id: string; name: string; principal: string; installments: number;
  installment_amount: string; confirmed_at: string; expense_id: string | null };
type Source = { id: string; name: string };
type Category = { key: string; name: string };
const money = (value: string, lang: 'pt' | 'en') =>
  new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency: 'BRL',
  }).format(Number(value));

export function ConfirmFinancing({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [name, setName] = useState('');
  const [value, setValue] = useState('120000');
  const [down, setDown] = useState('20000');
  const [installments, setInstallments] = useState('120');
  const [rate, setRate] = useState('12');
  const [recurring, setRecurring] = useState(false);
  const [account, setAccount] = useState('');
  const [category, setCategory] = useState('');
  const [firstDate, setFirstDate] = useState('');
  const [accounts, setAccounts] = useState<Source[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [debts, setDebts] = useState<Debt[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const requestId = useRef<string | null>(null);
  const headers = { Authorization: 'Bearer ' + token };
  const base = '/api/v1/auth';
  const load = useCallback(async () => {
    try {
      const [a, c, d] = await Promise.all([
        fetch(base + '/financial/sources', { headers }),
        fetch(base + '/categories', { headers }),
        fetch(base + '/financial/financing/confirmed', { headers }),
      ]);
      if (!a.ok || !c.ok || !d.ok) throw new Error('load');
      const sources = await a.json() as { accounts: Source[] };
      setAccounts(sources.accounts);
      setCategories(await c.json() as Category[]);
      setDebts(await d.json() as Debt[]);
    } catch {
      setError(pt ? 'Não foi possível consultar financiamentos.' : 'Could not load financings.');
    }
  }, [token, pt]);
  useEffect(() => { void load(); }, [load]);

  async function confirm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!window.confirm(pt
      ? 'CONFIRMA que o financiamento é REAL? O saldo devedor será incluído no patrimônio.'
      : 'CONFIRM this is a REAL financing? Its outstanding principal will be included in net worth.')) return;
    const key = requestId.current ?? crypto.randomUUID();
    requestId.current = key;
    setBusy(true); setError(''); setNotice('');
    try {
      const response = await fetch(base + '/financial/financing/confirm', {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json', 'Idempotency-Key': key },
        body: JSON.stringify({
          name: name.trim(), asset_value: value, down_payment: down,
          installments: Number(installments), annual_rate: rate,
          confirmation: 'CONFIRMAR FINANCIAMENTO REAL',
          create_recurring_expense: recurring,
          expense_category_key: recurring ? category : null,
          expense_account_id: recurring ? account : null,
          first_payment_on: recurring ? firstDate : null,
        }),
      });
      if (!response.ok) throw new Error('confirm');
      requestId.current = null;
      await load();
      window.dispatchEvent(new Event('finnova-financial-changed'));
      setNotice(pt ? 'Financiamento real registrado uma única vez.' :
        'Real financing recorded once.');
    } catch {
      setError(pt ? 'Falha na confirmação. Verifique os dados antes de reenviar.' :
        'Confirmation failed. Check the details before resubmitting.');
    } finally { setBusy(false); }
  }
  return <section className="profile" aria-labelledby="real-financing-heading">
    <h3 id="real-financing-heading">{pt ? 'Confirmar financiamento real' : 'Confirm a real financing'}</h3>
    <p>{pt ? 'Use apenas para uma dívida contratada de verdade. A simulação anterior não cria passivo.' :
      'Use only for a real contracted debt. Simulations do not create liabilities.'}</p>
    <form onSubmit={event => void confirm(event)}>
      <fieldset disabled={busy}>
        <legend>{pt ? 'Dados reais para confirmação' : 'Real contract details'}</legend>
        <label>{pt ? 'Identificação do financiamento' : 'Financing label'}
          <input required maxLength={100} value={name} onChange={event => { setName(event.target.value); requestId.current = null; }} />
        </label>
        <label>{pt ? 'Valor do bem (R$)' : 'Asset price (BRL)'}
          <input type="number" min="0.01" step="0.01" required value={value}
            onChange={event => { setValue(event.target.value); requestId.current = null; }} />
        </label>
        <label>{pt ? 'Entrada (R$)' : 'Down payment (BRL)'}
          <input type="number" min="0" step="0.01" required value={down}
            onChange={event => { setDown(event.target.value); requestId.current = null; }} />
        </label>
        <label>{pt ? 'Número de parcelas' : 'Installments'}
          <input type="number" min="1" max="600" step="1" required value={installments}
            onChange={event => { setInstallments(event.target.value); requestId.current = null; }} />
        </label>
        <label>{pt ? 'Taxa efetiva anual (%)' : 'Effective annual rate (%)'}
          <input type="number" min="0" max="100" step="0.000001" required value={rate}
            onChange={event => { setRate(event.target.value); requestId.current = null; }} />
        </label>
        <label><input type="checkbox" checked={recurring}
          onChange={event => { setRecurring(event.target.checked); requestId.current = null; }} />
          {pt ? 'Criar também a primeira parcela como despesa recorrente' :
            'Also create the first installment as a recurring expense'}</label>
        {recurring && <>
          <label>{pt ? 'Conta de pagamento' : 'Payment account'}
            <select required value={account} onChange={event => { setAccount(event.target.value); requestId.current = null; }}>
              <option value="">{pt ? 'Selecione' : 'Select'}</option>
              {accounts.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </label>
          <label>{pt ? 'Categoria da despesa' : 'Expense category'}
            <select required value={category} onChange={event => { setCategory(event.target.value); requestId.current = null; }}>
              <option value="">{pt ? 'Selecione' : 'Select'}</option>
              {categories.map(c => <option key={c.key} value={c.key}>{c.name}</option>)}
            </select>
          </label>
          <label>{pt ? 'Data da primeira parcela' : 'First installment date'}
            <input required type="date" value={firstDate}
              onChange={event => { setFirstDate(event.target.value); requestId.current = null; }} />
          </label>
        </>}
      </fieldset>
      <p><strong>{pt ? 'Ao confirmar, o saldo financiado será registrado como passivo real.' :
        'On confirmation, the financed principal will be recorded as a real liability.'}</strong></p>
      <button type="submit" disabled={busy}>{pt ? 'Confirmar financiamento REAL' : 'Confirm REAL financing'}</button>
    </form>
    {error && <p role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
    <h4>{pt ? 'Financiamentos já confirmados' : 'Confirmed financings'}</h4>
    {debts.length === 0 ? <p>{pt ? 'Nenhum confirmado.' : 'None confirmed yet.'}</p> :
      <ul>{debts.map(d => <li key={d.id}>
        <strong>{d.name}</strong> — {pt ? 'saldo inicial' : 'initial principal'}:
        {' '}{money(d.principal, lang)}; {d.installments} {pt ? 'parcelas' : 'installments'};
        {' '}{pt ? 'parcela estimada' : 'estimated payment'}:
        {' '}{money(d.installment_amount, lang)}
        {d.expense_id && (pt ? ' (despesa recorrente vinculada)' : ' (linked recurring expense)')}
      </li>)}</ul>}
    <small>{pt
      ? 'Saldo devedor permanece no valor inicial até reconciliação futura aprovada. A recorrência registra a primeira despesa e a marca como recorrente; não amortiza automaticamente o passivo. Sem IOF, CET, seguros e tarifas. Não há reversão automática nesta etapa.'
      : 'Outstanding debt remains at initial principal pending an approved reconciliation feature. The recurring option creates the first expense as recurring; it does not automatically reduce the liability. Excludes taxes, insurance and fees. No automatic reversal in this release.'}</small>
  </section>;
}
