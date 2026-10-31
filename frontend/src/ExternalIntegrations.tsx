import { useCallback, useEffect, useState, type FormEvent } from 'react';

type Grant = { id: string; name: string; scopes: string[]; created_at: string;
  expires_at: string; revoked_at: string | null; last_used_at: string | null };
type Created = Grant & { api_key: string };

export function ExternalIntegrations({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [grants, setGrants] = useState<Grant[]>([]);
  const [name, setName] = useState('');
  const [balance, setBalance] = useState(true);
  const [worth, setWorth] = useState(false);
  const [issued, setIssued] = useState<Created | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const url = '/api/v1/external/grants';
  const headers = { Authorization: 'Bearer ' + token };
  const load = useCallback(async () => {
    try {
      const response = await fetch(url, { headers });
      if (!response.ok) throw new Error('load');
      setGrants(await response.json() as Grant[]);
    } catch {
      setError(pt ? 'Não foi possível carregar as integrações.' : 'Could not load integrations.');
    }
  }, [token, pt]);

  useEffect(() => { void load(); }, [load]);
  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setIssued(null); setError('');
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name, scopes: [
            ...(balance ? ['balance:read'] : []),
            ...(worth ? ['net_worth:read'] : []),
          ],
        }),
      });
      if (!response.ok) throw new Error('create');
      setIssued(await response.json() as Created);
      setName('');
      await load();
    } catch {
      setError(pt ? 'Não foi possível gerar a credencial.' : 'Could not issue credential.');
    } finally { setBusy(false); }
  }
  async function revoke(id: string) {
    if (!window.confirm(pt ? 'Revogar imediatamente esta chave?' : 'Revoke this key now?')) return;
    setError('');
    try {
      const response = await fetch(url + '/' + encodeURIComponent(id), {
        method: 'DELETE', headers,
      });
      if (!response.ok) throw new Error('revoke');
      setIssued(null);
      await load();
    } catch {
      setError(pt ? 'Não foi possível revogar a chave.' : 'Could not revoke key.');
    }
  }
  return <section className="profile" aria-labelledby="external-api-heading">
    <h3 id="external-api-heading">{pt ? 'Integrações externas (API)' : 'External integrations (API)'}</h3>
    <p>{pt
      ? 'Conceda somente leituras agregadas a uma integração de confiança. Cada chave vale até 90 dias e permite até 30 consultas por minuto; nunca autoriza alterações financeiras.'
      : 'Grant only aggregate read access to a trusted integration. Keys expire within 90 days and permit up to 30 requests per minute; financial changes are never allowed.'}</p>
    <form onSubmit={event => void create(event)}>
      <fieldset disabled={busy}>
        <legend>{pt ? 'Nova chave de integração' : 'New integration key'}</legend>
        <label>{pt ? 'Nome da integração' : 'Integration name'}
          <input required maxLength={60} value={name} onChange={e => setName(e.target.value)} />
        </label>
        <label><input type="checkbox" checked={balance} onChange={e => setBalance(e.target.checked)} />
          {pt ? 'Ler saldo mensal agregado' : 'Read aggregate monthly balance'}</label>
        <label><input type="checkbox" checked={worth} onChange={e => setWorth(e.target.checked)} />
          {pt ? 'Ler totais do patrimônio' : 'Read net worth totals'}</label>
      </fieldset>
      <button type="submit" disabled={busy || (!balance && !worth)}>
        {pt ? 'Gerar chave' : 'Create key'}
      </button>
    </form>
    {issued && <div role="status">
      <p><strong>{pt ? 'Copie agora: a chave não será exibida novamente.' :
        'Copy now: this key will never be shown again.'}</strong></p>
      <code style={{ overflowWrap: 'anywhere', userSelect: 'all' }}>{issued.api_key}</code>
      <button className="secondary" type="button" onClick={() => {
        void navigator.clipboard?.writeText(issued.api_key);
      }}>{pt ? 'Copiar' : 'Copy'}</button>
      <button className="secondary" type="button" onClick={() => setIssued(null)}>
        {pt ? 'Ocultar chave' : 'Hide key'}</button>
    </div>}
    {error && <p role="alert">{error}</p>}
    <h4>{pt ? 'Chaves criadas' : 'Issued keys'}</h4>
    {grants.length === 0 ? <p>{pt ? 'Nenhuma integração cadastrada.' :
      'No integrations yet.'}</p> : <ul>{grants.map(g => <li key={g.id}>
      <strong>{g.name}</strong> ({g.scopes.join(', ')}) —
      {' '}{g.revoked_at ? (pt ? 'Revogada' : 'Revoked') :
        (pt ? 'Expira em ' : 'Expires ') + new Date(g.expires_at).toLocaleDateString(
          pt ? 'pt-BR' : 'en-US')}
      {!g.revoked_at && <button className="secondary" type="button"
        onClick={() => void revoke(g.id)}>{pt ? 'Revogar' : 'Revoke'}</button>}
    </li>)}</ul>}
    <small>{pt
      ? 'Contrato e exemplos disponíveis na documentação OpenAPI pública. Não envie sua chave por e-mail nem a inclua em URLs.'
      : 'Contract and examples are available in public OpenAPI documentation. Never email your key or place it in URLs.'}</small>
  </section>;
}
