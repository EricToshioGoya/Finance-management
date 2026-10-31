import { ContextualHelp } from './Education';
import { useCallback, useEffect, useState, type FormEvent } from 'react';

type InvestmentClass = 'fixed_income' | 'stocks' | 'fiis' | 'savings' | 'other';
type Row = {
  asset_class: InvestmentClass;
  amount: string;
  actual_percent: string | null;
  target_percent: string | null;
  deviation_points: string | null;
};
type Asset = { id: string; name: string; value: string; origin: string };
type ClassifiedAsset = Asset & { asset_class: InvestmentClass };
type Allocation = {
  total_invested: string;
  classes: Row[];
  unclassified: Asset[];
  classified: ClassifiedAsset[];
  has_targets: boolean;
};
const classes: InvestmentClass[] = ['fixed_income', 'stocks', 'fiis', 'savings', 'other'];
const names: Record<InvestmentClass, { pt: string; en: string }> = {
  fixed_income: { pt: 'Renda fixa', en: 'Fixed income' },
  stocks: { pt: 'Ações', en: 'Stocks' },
  fiis: { pt: 'FIIs', en: 'REITs' },
  savings: { pt: 'Poupança', en: 'Savings' },
  other: { pt: 'Outros investimentos', en: 'Other investments' },
};
const money = (value: string, lang: 'pt' | 'en') =>
  new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', { style: 'currency', currency: 'BRL' })
    .format(Number(value));

export function InvestmentAllocation({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [allocation, setAllocation] = useState<Allocation | null>(null);
  const [targets, setTargets] = useState<Record<InvestmentClass, string>>({
    fixed_income: '0', stocks: '0', fiis: '0', savings: '0', other: '0',
  });
  const [pendingClasses, setPendingClasses] = useState<Record<string, InvestmentClass>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const requestAllocation = useCallback(async (path: string, method = 'GET', body?: object) => {
    const response = await fetch('/api/v1/auth/financial/investment-allocation' + path, {
      method,
      headers: {
        Authorization: 'Bearer ' + token,
        ...(body ? { 'Content-Type': 'application/json' } : {}),
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
    if (!response.ok) throw new Error('allocation_request_failed');
    return response.json() as Promise<Allocation>;
  }, [token]);

  const reload = useCallback(async () => {
    try {
      const data = await requestAllocation('');
      setAllocation(data);
      setError('');
    } catch { setError(pt ? 'Não foi possível consultar a alocação.' : 'Could not load allocation.'); }
  }, [pt, requestAllocation]);

  useEffect(() => {
    void reload();
    const refresh = () => { if (document.visibilityState === 'visible') void reload(); };
    const interval = window.setInterval(refresh, 30000);
    document.addEventListener('visibilitychange', refresh);
    window.addEventListener('finnova-financial-changed', refresh);
    return () => {
      window.clearInterval(interval);
      document.removeEventListener('visibilitychange', refresh);
      window.removeEventListener('finnova-financial-changed', refresh);
    };
  }, [reload]);

  useEffect(() => {
    if (!allocation?.has_targets) return;
    setTargets(Object.fromEntries(allocation.classes.map(row => [
      row.asset_class, row.target_percent ?? '0',
    ])) as Record<InvestmentClass, string>);
  }, [allocation]);

  async function saveTargets(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const sum = classes.reduce((total, key) => total + Number(targets[key]), 0);
    if (!classes.every(key => /^\d+(?:\.\d{1,2})?$/.test(targets[key]) &&
        Number(targets[key]) <= 100) || Math.abs(sum - 100) > 0.000001) {
      setError(pt ? 'Informe cinco alvos entre 0 e 100 cuja soma seja 100%.' :
        'Enter five targets from 0 to 100 that total exactly 100%.');
      return;
    }
    setBusy(true); setError(''); setNotice('');
    try {
      const data = await requestAllocation('/targets', 'PUT', { targets });
      setAllocation(data);
      setNotice(pt ? 'Metas percentuais salvas.' : 'Percentage targets saved.');
    } catch { setError(pt ? 'Não foi possível salvar as metas.' : 'Could not save targets.'); }
    finally { setBusy(false); }
  }

  async function assign(assetId: string, fallback: InvestmentClass = 'other') {
    setBusy(true); setError(''); setNotice('');
    try {
      const data = await requestAllocation('/assets/' + encodeURIComponent(assetId), 'PUT', {
        asset_class: pendingClasses[assetId] ?? fallback,
      });
      setAllocation(data);
      setNotice(pt ? 'Ativo classificado.' : 'Asset classified.');
    } catch { setError(pt ? 'Não foi possível classificar o ativo.' : 'Could not classify asset.'); }
    finally { setBusy(false); }
  }

  async function unassign(assetId: string) {
    setBusy(true); setError(''); setNotice('');
    try {
      const data = await requestAllocation('/assets/' + encodeURIComponent(assetId), 'DELETE');
      setAllocation(data);
      setNotice(pt ? 'Classificação removida; o ativo real foi preservado.' :
        'Classification removed; real asset retained.');
    } catch { setError(pt ? 'Não foi possível remover a classificação.' :
      'Could not remove classification.'); }
    finally { setBusy(false); }
  }

  return <section className="profile" aria-labelledby="investment-allocation-heading">
    <h3 id="investment-allocation-heading">{pt ? 'Alocação atual x alvo' : 'Current vs target allocation'} <ContextualHelp token={token} lang={lang} articleKey="diversification" /></h3>
    <p>{pt
      ? 'Compara apenas investimentos reais classificados. Saldo de conta corrente, dívidas e simulações não entram; itens manuais precisam de classificação explícita.'
      : 'Compares classified real investments only. Checking balances, debts, and projections are excluded; manual assets require explicit classification.'}</p>
    {error && <p role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
    {!allocation && !error && <p role="status">{pt ? 'Carregando…' : 'Loading…'}</p>}
    {allocation && <>
      <p><strong>{pt ? 'Total investido:' : 'Invested total:'}</strong> {money(allocation.total_invested, lang)}</p>
      {Number(allocation.total_invested) <= 0 && <p role="status">
        {pt ? 'Sem investimentos classificados: percentuais e desvios indisponíveis.' :
          'No classified investments: percentages and deviations unavailable.'}
      </p>}
      <div className="allocation-bars" role="group" aria-label={pt ? 'Comparação da alocação por classe' : 'Allocation by class'}>
        {allocation.classes.map(row => <div key={row.asset_class} style={{ marginBottom: 12 }}>
          <strong>{names[row.asset_class][lang]}</strong>
          <div style={{ display: 'grid', gridTemplateColumns: '72px 1fr 68px', gap: 8, alignItems: 'center' }}>
            <span>{pt ? 'Atual' : 'Actual'}</span>
            <div style={{ background: 'rgba(120,120,120,.15)', height: 13, borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ width: `${row.actual_percent ?? 0}%`, height: '100%', background: '#16806c' }} />
            </div><span>{row.actual_percent === null ? '—' : row.actual_percent + '%'}</span>
            <span>{pt ? 'Alvo' : 'Target'}</span>
            <div style={{ background: 'rgba(120,120,120,.15)', height: 13, borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ width: `${row.target_percent ?? 0}%`, height: '100%', background: '#2563eb' }} />
            </div><span>{row.target_percent === null ? '—' : row.target_percent + '%'}</span>
          </div>
        </div>)}
      </div>
      <div className="indicator-table-wrap" tabIndex={0}><table>
        <caption>{pt ? 'Distribuição real e desvios em pontos percentuais' :
          'Actual distribution and deviations in percentage points'}</caption>
        <thead><tr><th>{pt ? 'Classe' : 'Class'}</th><th>BRL</th>
          <th>{pt ? 'Atual' : 'Actual'}</th><th>{pt ? 'Alvo' : 'Target'}</th>
          <th>{pt ? 'Desvio (p.p.)' : 'Deviation (pp)'}</th></tr></thead>
        <tbody>{allocation.classes.map(row => <tr key={row.asset_class}>
          <th scope="row">{names[row.asset_class][lang]}</th>
          <td>{money(row.amount, lang)}</td>
          <td>{row.actual_percent === null ? '—' : row.actual_percent + '%'}</td>
          <td>{row.target_percent === null ? '—' : row.target_percent + '%'}</td>
          <td>{row.deviation_points === null ? '—' : row.deviation_points}</td>
        </tr>)}</tbody>
      </table></div>
      <form onSubmit={event => void saveTargets(event)} aria-busy={busy}>
        <fieldset disabled={busy}>
          <legend>{pt ? 'Definir alvos (soma obrigatória: 100%)' :
            'Set target percentages (must total 100%)'}</legend>
          {classes.map(key => <label key={key} style={{ display: 'inline-flex', margin: 6, gap: 4, alignItems: 'center' }}>
            {names[key][lang]}
            <input style={{ maxWidth: 85 }} type="number" min="0" max="100" step="0.01"
              value={targets[key]} required onChange={event =>
                setTargets(current => ({ ...current, [key]: event.target.value }))} />
            %
          </label>)}
        </fieldset>
        <button type="submit" disabled={busy}>{pt ? 'Salvar alocação-alvo' : 'Save target allocation'}</button>
      </form>
      {allocation.classified.length > 0 && <div>
        <h4>{pt ? 'Investimentos manuais classificados' : 'Classified manual investments'}</h4>
        {allocation.classified.map(asset => <div key={asset.id}
          style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center', marginBottom: 8 }}>
          <span>{asset.name} — {money(asset.value, lang)}</span>
          <label>
            <span className="sr-only">{pt ? 'Alterar classe de' : 'Change class for'} {asset.name}</span>
            <select value={pendingClasses[asset.id] ?? asset.asset_class}
              onChange={event => setPendingClasses(current => ({ ...current,
                [asset.id]: event.target.value as InvestmentClass }))}>
              {classes.map(key => <option value={key} key={key}>{names[key][lang]}</option>)}
            </select>
          </label>
          <button type="button" className="secondary" disabled={busy}
            onClick={() => void assign(asset.id, asset.asset_class)}>
            {pt ? 'Atualizar classe' : 'Update class'}
          </button>
          <button type="button" className="secondary" disabled={busy}
            onClick={() => void unassign(asset.id)}>
            {pt ? 'Remover classificação' : 'Remove classification'}
          </button>
        </div>)}
      </div>}
      {allocation.unclassified.length > 0 && <div>
        <h4>{pt ? 'Ativos manuais ainda não classificados' : 'Unclassified manual assets'}</h4>
        <p>{pt ? 'Classifique apenas os itens que são investimentos reais.' :
          'Only classify assets that are real investments.'}</p>
        {allocation.unclassified.map(asset => <div key={asset.id} style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center', marginBottom: 8 }}>
          <span>{asset.name} — {money(asset.value, lang)}</span>
          <label>
            <span className="sr-only">{pt ? 'Classe para' : 'Class for'} {asset.name}</span>
            <select value={pendingClasses[asset.id] ?? 'other'}
              onChange={event => setPendingClasses(current => ({ ...current,
                [asset.id]: event.target.value as InvestmentClass }))}>
              {classes.map(key => <option value={key} key={key}>{names[key][lang]}</option>)}
            </select>
          </label>
          <button type="button" className="secondary" disabled={busy} onClick={() => void assign(asset.id)}>
            {pt ? 'Classificar' : 'Classify'}
          </button>
        </div>)}
      </div>}
    </>}
  </section>;
}
