import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, errorText, idempotent, money, shortDate, today, type Lang } from './api';

type Account = { id: string; name: string };
type Card = { id: string; name: string };
type Category = { key: string; name: string; color: string; active: boolean };
type Recurring = { id: string; description: string; amount: string; account_id: string | null; starts_on: string };
type OneTime = { id: string; description: string; amount: string; account_id: string | null; occurred_on: string };
type Bonus = { id: string; description: string; amount: string; periodicity: 'monthly' | 'annual'; starts_on: string; reference_month: number | null };
type Expense = { id: string; description: string; amount: string; category_key: string; occurred_on: string; recurring: boolean; account_id: string | null; credit_card_id: string | null };
type Kind = 'expense' | 'one-time' | 'recurring' | 'bonus';

/** Lançamentos: despesas (SPEC-059), receitas recorrentes/pontuais (SPEC-056/057), bônus (SPEC-058) e edição/exclusão (SPEC-006). */
export function Transactions({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [kind, setKind] = useState<Kind>('expense');
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [cards, setCards] = useState<Card[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [recurring, setRecurring] = useState<Recurring[]>([]);
  const [oneTime, setOneTime] = useState<OneTime[]>([]);
  const [bonuses, setBonuses] = useState<Bonus[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [editing, setEditing] = useState<Expense | null>(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const [sources, cats, rec, one, bon, exp] = await Promise.all([
        api<{ accounts: Account[]; credit_cards: Card[] }>(token, '/financial/sources'),
        api<Category[]>(token, '/categories'),
        api<Recurring[]>(token, '/financial/recurring-incomes'),
        api<OneTime[]>(token, '/financial/one-time-incomes'),
        api<Bonus[]>(token, '/financial/bonuses'),
        api<Expense[]>(token, '/financial/expenses'),
      ]);
      setAccounts(sources.accounts); setCards(sources.credit_cards); setCategories(cats.filter(item => item.active));
      setRecurring(rec); setOneTime(one); setBonuses(bon); setExpenses(exp);
    } catch (cause) { setError(errorText(cause, lang)); }
  }, [token, lang]);
  useEffect(() => { void load(); }, [load]);

  async function run(action: () => Promise<unknown>, done: string, form?: HTMLFormElement) {
    setBusy(true); setError(''); setStatus('');
    try { await action(); form?.reset(); setEditing(null); setStatus(done); await load(); }
    catch (cause) { setError(errorText(cause, lang)); }
    finally { setBusy(false); }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form)) as Record<string, string>;
    const account = data.account || null;
    if (kind === 'expense') {
      const origin = data.origin ?? '';
      const body = {
        description: data.description, amount: data.amount, category_key: data.category,
        occurred_on: data.date, recurring: data.recurring === 'on',
      };
      if (editing) {
        void run(() => api(token, `/financial/expenses/${editing.id}`, { method: 'PATCH', body: JSON.stringify(body) }), pt ? 'Despesa atualizada.' : 'Expense updated.', form);
      } else {
        void run(() => api(token, '/financial/expenses', { method: 'POST', headers: idempotent(), body: JSON.stringify({
          ...body,
          account_id: origin.startsWith('a:') ? origin.slice(2) : null,
          credit_card_id: origin.startsWith('c:') ? origin.slice(2) : null,
        }) }), pt ? 'Despesa registrada.' : 'Expense saved.', form);
      }
    } else if (kind === 'one-time') {
      void run(() => api(token, '/financial/one-time-incomes', { method: 'POST', headers: idempotent(), body: JSON.stringify({ description: data.description, amount: data.amount, occurred_on: data.date, account_id: account }) }), pt ? 'Receita registrada.' : 'Income saved.', form);
    } else if (kind === 'recurring') {
      void run(() => api(token, '/financial/recurring-incomes', { method: 'POST', headers: idempotent(), body: JSON.stringify({ description: data.description, amount: data.amount, starts_on: data.date || null, account_id: account }) }), pt ? 'Receita recorrente registrada.' : 'Recurring income saved.', form);
    } else {
      void run(() => api(token, '/financial/bonuses', { method: 'POST', headers: idempotent(), body: JSON.stringify({
        description: data.description, amount: data.amount, periodicity: data.periodicity,
        starts_on: data.date || null, reference_month: data.periodicity === 'annual' ? Number(data.month) : null,
      }) }), pt ? 'Bônus registrado.' : 'Bonus saved.', form);
    }
  }

  // SPEC-006-R04: exclusão só após confirmação explícita do usuário.
  const remove = (path: string, label: string) => {
    if (!window.confirm(pt ? `Excluir "${label}"? Esta ação não pode ser desfeita.` : `Delete "${label}"? This cannot be undone.`)) return;
    void run(() => api(token, path, { method: 'DELETE' }), pt ? 'Lançamento excluído.' : 'Entry deleted.');
  };
  const categoryName = (key: string) => categories.find(item => item.key === key)?.name ?? key;
  const tabs: [Kind, string][] = [['expense', pt ? 'Despesa' : 'Expense'], ['one-time', pt ? 'Receita pontual' : 'One-time income'], ['recurring', pt ? 'Receita recorrente' : 'Recurring income'], ['bonus', pt ? 'Bônus/PLR' : 'Bonus']];
  const rows = [
    ...expenses.map(item => ({ id: item.id, date: item.occurred_on, label: item.description, detail: `${categoryName(item.category_key)}${item.recurring ? (pt ? ' · recorrente' : ' · recurring') : ''}`, amount: -Number(item.amount), path: `/financial/expenses/${item.id}`, expense: item })),
    ...oneTime.map(item => ({ id: item.id, date: item.occurred_on, label: item.description, detail: pt ? 'Receita pontual' : 'One-time income', amount: Number(item.amount), path: `/financial/one-time-incomes/${item.id}`, expense: null })),
    ...recurring.map(item => ({ id: item.id, date: item.starts_on, label: item.description, detail: pt ? 'Receita mensal recorrente' : 'Monthly recurring income', amount: Number(item.amount), path: `/financial/recurring-incomes/${item.id}`, expense: null })),
    ...bonuses.map(item => ({ id: item.id, date: item.starts_on, label: item.description, detail: item.periodicity === 'annual' ? `${pt ? 'Bônus anual · mês' : 'Annual bonus · month'} ${item.reference_month}` : (pt ? 'Bônus mensal' : 'Monthly bonus'), amount: Number(item.amount), path: `/financial/bonuses/${item.id}`, expense: null })),
  ].sort((a, b) => b.date.localeCompare(a.date));

  return <div className="stack">
    <section className="profile" aria-labelledby="new-entry-title">
      <h3 id="new-entry-title">{editing ? (pt ? 'Editar despesa' : 'Edit expense') : (pt ? 'Novo lançamento' : 'New entry')}</h3>
      {!editing && <div className="segmented" role="group" aria-label={pt ? 'Tipo de lançamento' : 'Entry type'}>
        {tabs.map(([value, label]) => <button key={value} type="button" aria-pressed={kind === value} onClick={() => { setKind(value); setStatus(''); }}>{label}</button>)}
      </div>}
      <form onSubmit={submit} className="form-grid" key={`${kind}-${editing?.id ?? 'new'}`} aria-busy={busy}>
        <div className="field"><label htmlFor="tx-description">{pt ? 'Descrição' : 'Description'}</label><input id="tx-description" name="description" maxLength={100} required defaultValue={editing?.description} /></div>
        <div className="field"><label htmlFor="tx-amount">{pt ? 'Valor (R$)' : 'Amount (BRL)'}</label><input id="tx-amount" name="amount" type="number" min={kind === 'bonus' ? '0' : '0.01'} step="0.01" required defaultValue={editing?.amount} /></div>
        <div className="field"><label htmlFor="tx-date">{kind === 'recurring' || kind === 'bonus' ? (pt ? 'Início (opcional)' : 'Start (optional)') : (pt ? 'Data' : 'Date')}</label>
          <input id="tx-date" name="date" type="date" required={kind === 'expense' || kind === 'one-time'} defaultValue={editing?.occurred_on ?? (kind === 'expense' || kind === 'one-time' ? today() : undefined)} /></div>
        {kind === 'expense' && <div className="field"><label htmlFor="tx-category">{pt ? 'Categoria' : 'Category'}</label>
          <select id="tx-category" name="category" required defaultValue={editing?.category_key ?? ''}><option value="" disabled>{pt ? 'Selecione' : 'Select'}</option>{categories.map(item => <option key={item.key} value={item.key}>{item.name}</option>)}</select></div>}
        {kind === 'expense' && !editing && <div className="field"><label htmlFor="tx-origin">{pt ? 'Pago com' : 'Paid with'}</label>
          <select id="tx-origin" name="origin" required defaultValue=""><option value="" disabled>{pt ? 'Selecione a conta ou o cartão' : 'Select the account or card'}</option>
            {accounts.map(item => <option key={item.id} value={`a:${item.id}`}>{pt ? 'Conta' : 'Account'}: {item.name}</option>)}
            {cards.map(item => <option key={item.id} value={`c:${item.id}`}>{pt ? 'Cartão' : 'Card'}: {item.name}</option>)}</select></div>}
        {(kind === 'one-time' || kind === 'recurring') && <div className="field"><label htmlFor="tx-account">{pt ? 'Conta de destino' : 'Destination account'}</label>
          <select id="tx-account" name="account" defaultValue=""><option value="">{pt ? 'Não informada' : 'Not specified'}</option>{accounts.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></div>}
        {kind === 'bonus' && <div className="field"><label htmlFor="tx-periodicity">{pt ? 'Periodicidade' : 'Frequency'}</label>
          <select id="tx-periodicity" name="periodicity" defaultValue="annual"><option value="annual">{pt ? 'Anual' : 'Annual'}</option><option value="monthly">{pt ? 'Mensal' : 'Monthly'}</option></select></div>}
        {kind === 'bonus' && <div className="field"><label htmlFor="tx-month">{pt ? 'Mês de referência (anual)' : 'Reference month (annual)'}</label><input id="tx-month" name="month" type="number" min="1" max="12" defaultValue="12" /></div>}
        {kind === 'expense' && <label className="check"><input type="checkbox" name="recurring" defaultChecked={editing?.recurring} />{pt ? 'Despesa recorrente (repete todo mês)' : 'Recurring expense (repeats monthly)'}</label>}
        <div className="actions">
          <button type="submit" disabled={busy}>{editing ? (pt ? 'Salvar alterações' : 'Save changes') : (pt ? 'Registrar' : 'Save')}</button>
          {editing && <button type="button" className="secondary" onClick={() => setEditing(null)}>{pt ? 'Cancelar' : 'Cancel'}</button>}
        </div>
      </form>
      <p className="message" role="status" aria-live="polite">{status}</p>
      {error && <p className="error" role="alert">{error}</p>}
    </section>

    <section className="profile" aria-labelledby="entries-title">
      <h3 id="entries-title">{pt ? 'Lançamentos' : 'Entries'}</h3>
      {rows.length === 0 ? <p>{pt ? 'Nenhum lançamento registrado.' : 'No entries yet.'}</p> : <div className="table-wrap" tabIndex={0}><table>
        <caption>{pt ? 'Receitas e despesas registradas, da mais recente para a mais antiga' : 'Recorded income and expenses, newest first'}</caption>
        <thead><tr><th>{pt ? 'Data' : 'Date'}</th><th>{pt ? 'Descrição' : 'Description'}</th><th>{pt ? 'Tipo' : 'Type'}</th><th className="num">{pt ? 'Valor' : 'Amount'}</th><th><span className="sr-only">{pt ? 'Ações' : 'Actions'}</span></th></tr></thead>
        <tbody>{rows.map(row => <tr key={row.id}>
          <td>{shortDate(row.date, lang)}</td><td>{row.label}</td><td>{row.detail}</td>
          <td className={`num ${row.amount < 0 ? 'negative' : 'positive'}`}>{money(row.amount, lang)}</td>
          <td className="row-actions">
            {row.expense && <button type="button" className="secondary" onClick={() => { setKind('expense'); setEditing(row.expense); }} aria-label={`${pt ? 'Editar' : 'Edit'} ${row.label}`}>{pt ? 'Editar' : 'Edit'}</button>}
            <button type="button" className="secondary danger" disabled={busy} onClick={() => remove(row.path, row.label)} aria-label={`${pt ? 'Excluir' : 'Delete'} ${row.label}`}>{pt ? 'Excluir' : 'Delete'}</button>
          </td>
        </tr>)}</tbody>
      </table></div>}
    </section>
  </div>;
}
