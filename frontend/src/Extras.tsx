import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, errorText, money, percent, shortDate, type Lang } from './api';

type Item = { id: string; kind: 'asset' | 'liability'; name: string; value: string; annual_rate: string | null; origin: string };
type NetWorth = { as_of: string; assets: Item[]; liabilities: Item[]; total_assets: string; total_liabilities: string; net_worth: string };

/** Patrimônio consolidado e itens manuais (SPEC-028). */
export function NetWorthItems({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [data, setData] = useState<NetWorth | null>(null);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    try { setData(await api<NetWorth>(token, '/financial/net-worth')); } catch (cause) { setError(errorText(cause, lang)); }
  }, [token, lang]);
  useEffect(() => { void load(); }, [load]);

  async function add(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget; const values = new FormData(form);
    setError('');
    try {
      await api(token, '/financial/net-worth/items', { method: 'POST', body: JSON.stringify({
        kind: values.get('nw-kind'), name: values.get('nw-name'), value: values.get('nw-value'), annual_rate: values.get('nw-rate') || null,
      }) });
      form.reset(); await load();
    } catch (cause) { setError(errorText(cause, lang)); }
  }
  async function remove(item: Item) {
    try { await api(token, `/financial/net-worth/items/${item.id}`, { method: 'DELETE' }); await load(); }
    catch (cause) { setError(errorText(cause, lang)); }
  }
  const origin = (value: string) => ({ manual: pt ? 'Manual' : 'Manual', account: pt ? 'Conta' : 'Account', credit_card_invoice: pt ? 'Fatura' : 'Card statement', financing: pt ? 'Financiamento' : 'Financing' }[value] ?? value);
  const table = (title: string, items: Item[]) => <div className="table-wrap" tabIndex={0}><table>
    <caption>{title}</caption>
    <thead><tr><th>{pt ? 'Nome' : 'Name'}</th><th>{pt ? 'Origem' : 'Source'}</th><th className="num">{pt ? 'Taxa a.a.' : 'Rate p.a.'}</th><th className="num">{pt ? 'Valor' : 'Value'}</th><th><span className="sr-only">{pt ? 'Ações' : 'Actions'}</span></th></tr></thead>
    <tbody>{items.map(item => <tr key={item.id}><td>{item.name}</td><td>{origin(item.origin)}</td><td className="num">{item.annual_rate ? percent(item.annual_rate, lang) : '—'}</td><td className="num">{money(item.value, lang)}</td>
      <td className="row-actions">{item.origin === 'manual' && <button type="button" className="secondary danger" onClick={() => void remove(item)} aria-label={`${pt ? 'Excluir' : 'Delete'} ${item.name}`}>{pt ? 'Excluir' : 'Delete'}</button>}</td></tr>)}</tbody>
  </table></div>;
  return <section className="profile" aria-labelledby="net-worth-title">
    <h3 id="net-worth-title">{pt ? 'Patrimônio consolidado' : 'Consolidated net worth'}</h3>
    {error && <p className="error" role="alert">{error}</p>}
    {data && <>
      <div className="kpis">
        <div className="kpi"><span>{pt ? 'Ativos' : 'Assets'}</span><strong className="positive">{money(data.total_assets, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Passivos' : 'Liabilities'}</span><strong className="negative">{money(data.total_liabilities, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Patrimônio líquido' : 'Net worth'}</span><strong>{money(data.net_worth, lang)}</strong></div>
      </div>
      <div className="grid-2">{table(pt ? 'Ativos' : 'Assets', data.assets)}{table(pt ? 'Passivos' : 'Liabilities', data.liabilities)}</div>
    </>}
    <form onSubmit={add} className="form-grid">
      <div className="field"><label htmlFor="nw-kind">{pt ? 'Tipo' : 'Type'}</label><select id="nw-kind" name="nw-kind"><option value="asset">{pt ? 'Ativo' : 'Asset'}</option><option value="liability">{pt ? 'Passivo (dívida)' : 'Liability (debt)'}</option></select></div>
      <div className="field"><label htmlFor="nw-name">{pt ? 'Nome' : 'Name'}</label><input id="nw-name" name="nw-name" maxLength={100} required /></div>
      <div className="field"><label htmlFor="nw-value">{pt ? 'Valor (R$)' : 'Value (BRL)'}</label><input id="nw-value" name="nw-value" type="number" min="0.01" step="0.01" required /></div>
      <div className="field"><label htmlFor="nw-rate">{pt ? 'Taxa anual (%) opcional' : 'Annual rate (%) optional'}</label><input id="nw-rate" name="nw-rate" type="number" min="0" step="0.01" /></div>
      <div className="actions"><button type="submit">{pt ? 'Adicionar item' : 'Add item'}</button></div>
    </form>
  </section>;
}

type Notification = { id: string; kind: string; title: string; message: string; created_at: string; read_at: string | null };
type Preference = { kind: string; enabled: boolean };
const kindNames: Record<string, [string, string]> = {
  invoice_due: ['Vencimento de fatura', 'Card statement due'], budget_goal_exceeded: ['Meta de orçamento excedida', 'Budget goal exceeded'],
  watchlist_document: ['Novo documento de empresa acompanhada', 'New document from a watched company'], recurring_expense_due: ['Despesa recorrente a vencer', 'Recurring expense due'],
};

/** Central de notificações in-app e preferências por tipo (SPEC-039). */
export function Notifications({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [items, setItems] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<Preference[]>([]);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    try {
      const [list, prefs] = await Promise.all([api<Notification[]>(token, '/api/v1/notifications'), api<Preference[]>(token, '/api/v1/notifications/preferences')]);
      setItems(list); setPreferences(prefs);
    } catch (cause) { setError(errorText(cause, lang)); }
  }, [token, lang]);
  useEffect(() => { void load(); }, [load]);
  const markRead = async (item: Notification) => { await api(token, `/api/v1/notifications/${item.id}/read`, { method: 'PATCH' }).catch(() => undefined); await load(); };
  const toggle = async (preference: Preference) => { await api(token, `/api/v1/notifications/preferences/${preference.kind}`, { method: 'PUT', body: JSON.stringify({ enabled: !preference.enabled }) }).catch(() => undefined); await load(); };
  const unread = items.filter(item => !item.read_at).length;
  return <section className="profile" aria-labelledby="notifications-title">
    <h3 id="notifications-title">{pt ? 'Notificações' : 'Notifications'} {unread > 0 && <span className="badge">{unread}</span>}</h3>
    {error && <p className="error" role="alert">{error}</p>}
    {items.length === 0 ? <p>{pt ? 'Nenhuma notificação.' : 'No notifications.'}</p> : <ul className="notice-list">{items.map(item => <li key={item.id} className={item.read_at ? 'read' : ''}>
      <div><strong>{item.title}</strong><span>{item.message}</span><small>{shortDate(item.created_at, lang)}</small></div>
      {!item.read_at && <button type="button" className="secondary" onClick={() => void markRead(item)}>{pt ? 'Marcar como lida' : 'Mark as read'}</button>}
    </li>)}</ul>}
    <details><summary>{pt ? 'Tipos de alerta' : 'Alert types'}</summary>
      {preferences.map(preference => <label className="check" key={preference.kind}><input type="checkbox" checked={preference.enabled} onChange={() => void toggle(preference)} />{(kindNames[preference.kind] ?? [preference.kind, preference.kind])[pt ? 0 : 1]}</label>)}
    </details>
  </section>;
}

type Company = { id: string; ticker: string; legal_name: string; sector: string };
type Watch = { company: Company; created_at: string };

/** Watchlist de empresas (SPEC-027). */
export function Watchlist({ token, lang, version }: { token: string; lang: Lang; version: number }) {
  const pt = lang === 'pt';
  const [items, setItems] = useState<Watch[]>([]);
  const load = useCallback(async () => { setItems(await api<Watch[]>(token, '/api/v1/companies/watchlist').catch(() => [])); }, [token]);
  useEffect(() => { void load(); }, [load, version]);
  return <section className="profile" aria-labelledby="watchlist-title">
    <h3 id="watchlist-title">{pt ? 'Empresas acompanhadas' : 'Watched companies'}</h3>
    {items.length === 0 ? <p>{pt ? 'Pesquise uma empresa e clique em "Acompanhar" para receber avisos de novos documentos.' : 'Search for a company and click "Watch" to be notified of new documents.'}</p>
      : <ul className="source-list">{items.map(item => <li key={item.company.id}><strong>{item.company.ticker}</strong><span>{item.company.legal_name} · {item.company.sector}</span>
        <button type="button" className="secondary" onClick={() => void api(token, `/api/v1/companies/${item.company.id}/watchlist`, { method: 'DELETE' }).then(load)}>{pt ? 'Deixar de acompanhar' : 'Unwatch'}</button></li>)}</ul>}
  </section>;
}

type Engagement = { start: string; end: string; modules: { module: string; accesses: number; unique_users: number }[]; most_used_module: string | null; dau: number; wau: number; mau: number; average_frequency: number; inactive_users: number; inactive_days: number };

/** Uso por módulo e engajamento para administradores (SPEC-043). */
export function AdminEngagement({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [data, setData] = useState<Engagement | null>(null);
  useEffect(() => { void api<Engagement>(token, '/api/v1/admin/engagement').then(setData).catch(() => setData(null)); }, [token]);
  if (!data) return null;
  const peak = Math.max(1, ...data.modules.map(item => item.accesses));
  return <section className="profile" aria-labelledby="engagement-title">
    <h3 id="engagement-title">{pt ? 'Uso e engajamento' : 'Usage and engagement'}</h3>
    <div className="kpis">
      <div className="kpi"><span>DAU</span><strong>{data.dau}</strong></div><div className="kpi"><span>WAU</span><strong>{data.wau}</strong></div>
      <div className="kpi"><span>MAU</span><strong>{data.mau}</strong></div>
      <div className="kpi"><span>{pt ? 'Inativos' : 'Inactive'} ({data.inactive_days}d)</span><strong>{data.inactive_users}</strong></div>
    </div>
    <ul className="bar-list" aria-label={pt ? 'Acessos por módulo' : 'Accesses per module'}>{data.modules.map(item => <li key={item.module}><span>{item.module}</span><i style={{ width: `${item.accesses / peak * 100}%` }} /><b>{item.accesses}</b></li>)}</ul>
    <small>{pt ? 'Período' : 'Period'}: {shortDate(data.start, lang)} – {shortDate(data.end, lang)}</small>
  </section>;
}

type Distribution = { total_users: number; profiled_users: number; without_profile: number; items: { profile: string; count: number; percentage: string }[]; generated_at: string };
const profileColors: Record<string, string> = { conservador: '#2f8f6b', moderado: '#c27c0e', arrojado: '#a0451f' };
const profileNames: Record<string, [string, string]> = { conservador: ['Conservador', 'Conservative'], moderado: ['Moderado', 'Moderate'], arrojado: ['Arrojado', 'Aggressive'] };

/** Distribuição de perfis de investidor no painel administrativo (SPEC-062). */
export function AdminProfileDistribution({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [data, setData] = useState<Distribution | null>(null);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    const query = new URLSearchParams();
    if (start) query.set('start', start);
    if (end) query.set('end', end);
    try { setData(await api<Distribution>(token, `/api/v1/admin/investor-profiles?${query}`)); setError(''); }
    catch (cause) { setError(errorText(cause, lang)); }
  }, [token, start, end, lang]);
  // R05: atualização automática enquanto o painel estiver aberto.
  useEffect(() => { void load(); const timer = setInterval(() => void load(), 60000); return () => clearInterval(timer); }, [load]);
  const peak = Math.max(1, ...(data?.items.map(item => item.count) ?? []));
  return <section className="profile" aria-labelledby="profile-distribution-title">
    <h3 id="profile-distribution-title">{pt ? 'Distribuição de perfis de investidor' : 'Investor profile distribution'}</h3>
    <div className="inline-fields">
      <label className="inline-field">{pt ? 'Cadastro de' : 'Registered from'}<input type="date" value={start} onChange={event => setStart(event.target.value)} /></label>
      <label className="inline-field">{pt ? 'até' : 'to'}<input type="date" value={end} onChange={event => setEnd(event.target.value)} /></label>
    </div>
    {error && <p className="error" role="alert">{error}</p>}
    {data && <>
      <ul className="bar-list" aria-label={pt ? 'Usuários por perfil' : 'Users per profile'}>{data.items.map(item => <li key={item.profile}>
        <span>{(profileNames[item.profile] ?? [item.profile, item.profile])[pt ? 0 : 1]}</span>
        <i style={{ width: `${item.count / peak * 100}%`, background: profileColors[item.profile] }} />
        <b>{item.count} <small>({percent(item.percentage, lang, 1)})</small></b>
      </li>)}</ul>
      <p className="hint">{pt ? 'Usuários com perfil' : 'Users with a profile'}: {data.profiled_users} · {pt ? 'sem quiz respondido' : 'quiz not answered'}: {data.without_profile} · {pt ? 'atualizado em' : 'updated at'} {new Date(data.generated_at).toLocaleTimeString(pt ? 'pt-BR' : 'en-US')}</p>
    </>}
  </section>;
}
