import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, errorText, money, shortDate, type Lang } from './api';

type Overview = {
  active: { id: string; partner_name: string; since: string | null } | null;
  received: { id: string; from_name: string; expires_at: string }[];
  sent: { id: string; expires_at: string }[];
  history: { id: string; partner_name: string; ended_at: string | null }[];
};
type Item = { id: string; expense_id: string; description: string; amount: string; occurred_on: string; paid_by: 'me' | 'partner'; payer_percent: string; my_share: string; partner_share: string };
type Balance = { link_id: string; status: 'active' | 'ended'; partner_name: string; items: Item[]; settlements: { id: string; amount: string; paid_by: 'me' | 'partner'; created_at: string }[]; direction: 'settled' | 'partner_owes_me' | 'i_owe_partner'; amount: string };
type Expense = { id: string; description: string; amount: string; occurred_on: string };

/** Vínculo entre dois usuários (SPEC-044) e divisão de despesas com acertos (SPEC-045). */
export function Sharing({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [overview, setOverview] = useState<Overview | null>(null);
  const [balance, setBalance] = useState<Balance | null>(null);
  const [historyLink, setHistoryLink] = useState<string | null>(null);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [split, setSplit] = useState<'equal' | 'custom'>('equal');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const data = await api<Overview>(token, '/sharing');
      setOverview(data);
      const link = data.active?.id ?? historyLink;
      setBalance(link ? await api<Balance>(token, `/sharing/balance${data.active ? '' : `?link_id=${link}`}`) : null);
      setExpenses(await api<Expense[]>(token, '/financial/expenses'));
    } catch (cause) { setError(errorText(cause, lang)); }
  }, [token, lang, historyLink]);
  useEffect(() => { void load(); }, [load]);

  async function run(action: () => Promise<unknown>, done: string, form?: HTMLFormElement) {
    setError(''); setStatus('');
    try { await action(); form?.reset(); setStatus(done); await load(); }
    catch (cause) {
      const code = cause instanceof Error ? cause.message : '';
      const known: Record<string, [string, string]> = {
        self_invitation: ['Você não pode convidar a si mesmo.', 'You cannot invite yourself.'],
        already_linked: ['Já existe um vínculo ativo.', 'There is already an active link.'],
        invitation_expired: ['O convite expirou.', 'The invitation has expired.'],
        split_must_total_100: ['Os percentuais precisam somar 100%.', 'Percentages must add up to 100%.'],
        settlement_exceeds_balance: ['O acerto não pode superar o saldo pendente.', 'The settlement cannot exceed the pending balance.'],
        nothing_to_settle: ['Você não tem saldo a pagar.', 'You have nothing to pay.'],
        expense_already_shared: ['Essa despesa já está compartilhada.', 'This expense is already shared.'],
      };
      setError(known[code] ? known[code][pt ? 0 : 1] : errorText(cause, lang));
    }
  }

  const invite = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); const form = event.currentTarget;
    void run(() => api(token, '/sharing/invitations', { method: 'POST', body: JSON.stringify({ email: new FormData(form).get('share-email') }) }),
      pt ? 'Se o e-mail pertencer a um usuário verificado, o convite foi enviado.' : 'If the email belongs to a verified user, the invitation was sent.', form);
  };
  const shareExpense = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); const form = event.currentTarget; const data = new FormData(form);
    const payer = String(data.get('payer-percent') || '50');
    void run(() => api(token, '/sharing/expenses', { method: 'POST', body: JSON.stringify(split === 'equal'
      ? { expense_id: data.get('share-expense') }
      : { expense_id: data.get('share-expense'), split: 'custom', payer_percent: payer, partner_percent: String(100 - Number(payer)) }) }),
    pt ? 'Despesa compartilhada.' : 'Expense shared.', form);
  };
  const settle = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); const form = event.currentTarget;
    void run(() => api(token, '/sharing/settlements', { method: 'POST', headers: { 'Idempotency-Key': crypto.randomUUID() },
      body: JSON.stringify({ amount: new FormData(form).get('settle-amount'), link_id: balance?.link_id }) }), pt ? 'Acerto registrado.' : 'Settlement recorded.', form);
  };

  const sharedIds = new Set(balance?.items.map(item => item.expense_id) ?? []);
  const shareable = expenses.filter(item => !sharedIds.has(item.id));

  return <div className="stack">
    {error && <p className="error" role="alert">{error}</p>}
    <p className="message" role="status" aria-live="polite">{status}</p>
    <div className="grid-2">
      <section className="profile" aria-labelledby="link-title">
        <h3 id="link-title">{pt ? 'Conta compartilhada' : 'Shared account'}</h3>
        {overview?.active ? <>
          <p>{pt ? 'Vinculado com' : 'Linked with'} <strong>{overview.active.partner_name}</strong>{overview.active.since && ` ${pt ? 'desde' : 'since'} ${shortDate(overview.active.since, lang)}`}.</p>
          <p className="hint">{pt ? 'Somente despesas marcadas como compartilhadas ficam visíveis ao outro membro. Renda e demais gastos continuam privados.' : 'Only expenses marked as shared are visible to the other member. Income and other expenses stay private.'}</p>
          <button type="button" className="secondary danger" onClick={() => void run(() => api(token, `/sharing/links/${overview.active!.id}/end`, { method: 'POST' }), pt ? 'Vínculo desfeito. O histórico continua disponível.' : 'Link ended. History remains available.')}>{pt ? 'Desfazer vínculo' : 'End link'}</button>
        </> : <>
          <p className="hint">{pt ? 'Convide outra pessoa cadastrada para dividir despesas. O vínculo só é criado após o aceite.' : 'Invite another registered person to split expenses. The link is created only after acceptance.'}</p>
          <form onSubmit={invite}>
            <div className="field"><label htmlFor="share-email">{pt ? 'E-mail da pessoa' : 'Person’s email'}</label><input id="share-email" name="share-email" type="email" maxLength={254} required /></div>
            <button type="submit">{pt ? 'Enviar convite' : 'Send invitation'}</button>
          </form>
        </>}
        {!!overview?.received.length && <><h4>{pt ? 'Convites recebidos' : 'Invitations received'}</h4>
          <ul className="notice-list">{overview.received.map(item => <li key={item.id}><div><strong>{item.from_name}</strong><small>{pt ? 'Expira em' : 'Expires on'} {shortDate(item.expires_at, lang)}</small></div>
            <div className="actions"><button type="button" onClick={() => void run(() => api(token, `/sharing/invitations/${item.id}/accept`, { method: 'POST' }), pt ? 'Convite aceito.' : 'Invitation accepted.')}>{pt ? 'Aceitar' : 'Accept'}</button>
              <button type="button" className="secondary" onClick={() => void run(() => api(token, `/sharing/invitations/${item.id}/decline`, { method: 'POST' }), pt ? 'Convite recusado.' : 'Invitation declined.')}>{pt ? 'Recusar' : 'Decline'}</button></div></li>)}</ul></>}
        {!!overview?.sent.length && <><h4>{pt ? 'Convites enviados' : 'Invitations sent'}</h4>
          <ul className="notice-list">{overview.sent.map(item => <li key={item.id}><div><strong>{pt ? 'Aguardando aceite' : 'Awaiting acceptance'}</strong><small>{pt ? 'Expira em' : 'Expires on'} {shortDate(item.expires_at, lang)}</small></div>
            <button type="button" className="secondary" onClick={() => void run(() => api(token, `/sharing/invitations/${item.id}/cancel`, { method: 'POST' }), pt ? 'Convite cancelado.' : 'Invitation cancelled.')}>{pt ? 'Cancelar' : 'Cancel'}</button></li>)}</ul></>}
        {!!overview?.history.length && <div className="field"><label htmlFor="history-link">{pt ? 'Histórico de vínculos encerrados' : 'Ended links history'}</label>
          <select id="history-link" value={historyLink ?? ''} onChange={event => setHistoryLink(event.target.value || null)}>
            <option value="">{pt ? 'Selecione' : 'Select'}</option>{overview.history.map(item => <option key={item.id} value={item.id}>{item.partner_name}{item.ended_at ? ` — ${shortDate(item.ended_at, lang)}` : ''}</option>)}
          </select></div>}
      </section>

      {balance && <section className="profile" aria-labelledby="balance-title">
        <h3 id="balance-title">{pt ? 'Quem deve quem' : 'Who owes whom'}</h3>
        <div className="kpis"><div className="kpi">
          <span>{balance.status === 'ended' ? (pt ? 'Vínculo encerrado' : 'Link ended') : balance.partner_name}</span>
          <strong className={balance.direction === 'i_owe_partner' ? 'negative' : 'positive'}>{money(balance.amount, lang)}</strong>
          <small>{balance.direction === 'settled' ? (pt ? 'Tudo acertado' : 'All settled') : balance.direction === 'partner_owes_me' ? `${balance.partner_name} ${pt ? 'deve a você' : 'owes you'}` : `${pt ? 'Você deve a' : 'You owe'} ${balance.partner_name}`}</small>
        </div></div>
        {balance.direction === 'i_owe_partner' && <form onSubmit={settle} className="inline-fields">
          <div className="field"><label htmlFor="settle-amount">{pt ? 'Registrar acerto (R$)' : 'Record settlement (BRL)'}</label><input id="settle-amount" name="settle-amount" type="number" min="0.01" max={balance.amount} step="0.01" required /></div>
          <div className="actions"><button type="submit">{pt ? 'Registrar' : 'Record'}</button></div>
        </form>}
        {balance.status === 'active' && <form onSubmit={shareExpense}>
          <div className="field"><label htmlFor="share-expense">{pt ? 'Compartilhar uma despesa minha' : 'Share one of my expenses'}</label>
            <select id="share-expense" name="share-expense" required defaultValue=""><option value="" disabled>{pt ? 'Selecione' : 'Select'}</option>
              {shareable.map(item => <option key={item.id} value={item.id}>{item.description} · {money(item.amount, lang)} · {shortDate(item.occurred_on, lang)}</option>)}</select></div>
          <div className="segmented" role="group" aria-label={pt ? 'Divisão' : 'Split'}>
            <button type="button" aria-pressed={split === 'equal'} onClick={() => setSplit('equal')}>50/50</button>
            <button type="button" aria-pressed={split === 'custom'} onClick={() => setSplit('custom')}>{pt ? 'Percentual' : 'Custom'}</button>
          </div>
          {split === 'custom' && <div className="field"><label htmlFor="payer-percent">{pt ? 'Minha parte (%)' : 'My part (%)'}</label><input id="payer-percent" name="payer-percent" type="number" min="1" max="99" step="0.01" defaultValue="50" required /></div>}
          <button type="submit">{pt ? 'Compartilhar' : 'Share'}</button>
        </form>}
      </section>}
    </div>

    {balance && <section className="profile" aria-labelledby="composition-title">
      <h3 id="composition-title">{pt ? 'Composição do saldo' : 'Balance breakdown'}</h3>
      {balance.items.length === 0 ? <p>{pt ? 'Nenhuma despesa compartilhada.' : 'No shared expenses.'}</p> : <div className="table-wrap" tabIndex={0}><table>
        <caption>{pt ? 'Despesas compartilhadas e partes de cada membro' : 'Shared expenses and each member’s part'}</caption>
        <thead><tr><th>{pt ? 'Data' : 'Date'}</th><th>{pt ? 'Descrição' : 'Description'}</th><th>{pt ? 'Pago por' : 'Paid by'}</th><th className="num">{pt ? 'Total' : 'Total'}</th><th className="num">{pt ? 'Minha parte' : 'My part'}</th><th className="num">{balance.partner_name}</th><th><span className="sr-only">{pt ? 'Ações' : 'Actions'}</span></th></tr></thead>
        <tbody>{balance.items.map(item => <tr key={item.id}><td>{shortDate(item.occurred_on, lang)}</td><td>{item.description}</td><td>{item.paid_by === 'me' ? (pt ? 'Eu' : 'Me') : balance.partner_name}</td>
          <td className="num">{money(item.amount, lang)}</td><td className="num">{money(item.my_share, lang)}</td><td className="num">{money(item.partner_share, lang)}</td>
          <td className="row-actions">{item.paid_by === 'me' && balance.status === 'active' && <button type="button" className="secondary danger" onClick={() => void run(() => api(token, `/sharing/expenses/${item.id}`, { method: 'DELETE' }), pt ? 'Despesa deixou de ser compartilhada.' : 'Expense unshared.')} aria-label={`${pt ? 'Deixar de compartilhar' : 'Unshare'} ${item.description}`}>{pt ? 'Remover' : 'Remove'}</button>}</td></tr>)}</tbody>
      </table></div>}
      {balance.settlements.length > 0 && <ul className="source-list">{balance.settlements.map(item => <li key={item.id}><strong>{pt ? 'Acerto' : 'Settlement'} · {money(item.amount, lang)}</strong><span>{item.paid_by === 'me' ? (pt ? 'pago por mim' : 'paid by me') : `${pt ? 'pago por' : 'paid by'} ${balance.partner_name}`} · {shortDate(item.created_at, lang)}</span></li>)}</ul>}
    </section>}
  </div>;
}
