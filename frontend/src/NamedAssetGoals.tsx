import { ContextualHelp } from './Education';
import { useCallback, useEffect, useState, type FormEvent } from 'react';

type Asset = { id: string; name: string; value: string; kind: string; origin: string };
type Goal = {
  id: string;
  name: string;
  category: string;
  asset_id: string;
  asset_name: string;
  target_amount: string;
  deadline: string;
  annual_rate: string;
  current_value: string;
  progress_percent: string;
  remaining_amount: string;
  months_remaining: number;
  monthly_contribution_needed: string | null;
  projection_status: 'on_track' | 'needs_contribution' | 'overdue';
};
const categories = ['emergency', 'travel', 'home', 'education', 'other'] as const;
const labels: Record<string, { pt: string; en: string }> = {
  emergency: { pt: 'Reserva de emergência', en: 'Emergency reserve' },
  travel: { pt: 'Viagem', en: 'Travel' },
  home: { pt: 'Entrada de imóvel', en: 'Home down payment' },
  education: { pt: 'Educação', en: 'Education' },
  other: { pt: 'Outro', en: 'Other' },
};
const money = (value: string, lang: 'pt' | 'en') =>
  new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
    style: 'currency', currency: 'BRL',
  }).format(Number(value));

export function NamedAssetGoals({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [assets, setAssets] = useState<Asset[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [name, setName] = useState('');
  const [category, setCategory] = useState<(typeof categories)[number]>('emergency');
  const [assetId, setAssetId] = useState('');
  const [target, setTarget] = useState('');
  const [deadline, setDeadline] = useState('');
  const [rate, setRate] = useState('0');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const base = '/api/v1/auth/financial';
  const headers = { Authorization: 'Bearer ' + token };

  const load = useCallback(async () => {
    try {
      const [goalsResponse, worthResponse] = await Promise.all([
        fetch(base + '/named-asset-goals', { headers }),
        fetch(base + '/net-worth', { headers }),
      ]);
      if (!goalsResponse.ok || !worthResponse.ok) throw new Error('load');
      const goalData = await goalsResponse.json() as Goal[];
      const worthData = await worthResponse.json() as { assets: Asset[] };
      setGoals(goalData);
      setAssets(worthData.assets.filter(item => item.origin === 'manual'));
      setError('');
    } catch {
      setError(pt ? 'Não foi possível carregar as metas.' : 'Could not load goals.');
    }
  }, [token, pt]);

  useEffect(() => {
    void load();
    const refresh = () => { if (document.visibilityState === 'visible') void load(); };
    window.addEventListener('finnova-financial-changed', refresh);
    window.addEventListener('focus', refresh);
    return () => {
      window.removeEventListener('finnova-financial-changed', refresh);
      window.removeEventListener('focus', refresh);
    };
  }, [load]);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true); setError(''); setNotice('');
    try {
      const response = await fetch(base + '/named-asset-goals', {
        method: 'POST',
        headers: { ...headers, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(), category, asset_id: assetId,
          target_amount: target, deadline, annual_rate: rate,
        }),
      });
      if (!response.ok) throw new Error('create');
      setName(''); setTarget(''); setDeadline(''); setRate('0');
      await load();
      setNotice(pt ? 'Meta criada e vinculada ao ativo real.' : 'Goal linked to real asset.');
    } catch {
      setError(pt ? 'Não foi possível criar. Verifique ativo, valor e prazo futuro.' :
        'Could not create goal. Check asset, amount and future deadline.');
    } finally { setBusy(false); }
  }

  async function remove(id: string) {
    if (!window.confirm(pt ? 'Excluir esta meta? O ativo será preservado.' :
      'Delete this goal? The asset will remain.')) return;
    setBusy(true); setError(''); setNotice('');
    try {
      const response = await fetch(base + '/named-asset-goals/' + encodeURIComponent(id), {
        method: 'DELETE', headers,
      });
      if (!response.ok) throw new Error('delete');
      await load();
      setNotice(pt ? 'Meta excluída; ativo preservado.' : 'Goal deleted; asset retained.');
    } catch {
      setError(pt ? 'Não foi possível excluir a meta.' : 'Could not delete goal.');
    } finally { setBusy(false); }
  }

  return <section className="profile" aria-labelledby="named-goals-heading">
    <h3 id="named-goals-heading">{pt ? 'Metas nomeadas por ativo' : 'Named asset goals'}</h3>
    <p>{pt
      ? 'Acompanhe o valor real de um ativo manual e o aporte projetado para atingir sua meta. Nenhum valor é movimentado.'
      : 'Track the real value of a manual asset and projected contributions. No money is moved.'}</p>
    {error && <p role="alert">{error}</p>}
    {notice && <p role="status">{notice}</p>}
    <form onSubmit={event => void create(event)}>
      <fieldset disabled={busy || assets.length === 0}>
        <legend>{pt ? 'Criar meta' : 'Create goal'}</legend>
        <label>{pt ? 'Nome da meta' : 'Goal name'}
          <input required maxLength={100} value={name}
            onChange={event => setName(event.target.value)} />
        </label>
        <label>{pt ? 'Categoria' : 'Category'}
          <select value={category} onChange={event =>
            setCategory(event.target.value as (typeof categories)[number])}>
            {categories.map(key => <option key={key} value={key}>{labels[key][lang]}</option>)}
          </select>
        </label>
        <label>{pt ? 'Ativo real vinculado' : 'Linked real asset'}
          <select required value={assetId} onChange={event => setAssetId(event.target.value)}>
            <option value="">{pt ? 'Selecione um ativo' : 'Select asset'}</option>
            {assets.map(asset => <option key={asset.id} value={asset.id}>
              {asset.name} — {money(asset.value, lang)}
            </option>)}
          </select>
        </label>
        <label>{pt ? 'Valor-alvo (BRL)' : 'Target amount (BRL)'}
          <input required type="number" min="0.01" step="0.01" value={target}
            onChange={event => setTarget(event.target.value)} />
        </label>
        <label>{pt ? 'Prazo final' : 'Deadline'}
          <input required type="date" value={deadline} onChange={event => setDeadline(event.target.value)} />
        </label>
        <label>{pt ? 'Hipótese de retorno anual (%)' : 'Assumed annual return (%)'} <ContextualHelp token={token} lang={lang} articleKey="interest-rate" />
          <input required type="number" min="0" max="100" step="0.000001" value={rate}
            onChange={event => setRate(event.target.value)} />
        </label>
      </fieldset>
      {assets.length === 0 && <p>
        {pt ? 'Cadastre um ativo manual no patrimônio real antes de criar a meta.' :
          'Add a manual real asset to your net worth before creating a goal.'}
      </p>}
      <button disabled={busy || assets.length === 0} type="submit">
        {pt ? 'Vincular e criar meta' : 'Link and create goal'}
      </button>
    </form>
    {goals.length === 0 && <p>{pt ? 'Nenhuma meta cadastrada.' : 'No goals yet.'}</p>}
    {goals.map(goal => <article key={goal.id} style={{ marginTop: 18, marginBottom: 18 }}>
      <h4>{goal.name} — {labels[goal.category]?.[lang] ?? goal.category}</h4>
      <p>{pt ? 'Ativo' : 'Asset'}: {goal.asset_name}.{' '}
        {pt ? 'Acumulado real' : 'Real accumulated value'}: {money(goal.current_value, lang)} /
        {' '}{money(goal.target_amount, lang)}</p>
      <div role="progressbar" aria-label={goal.name}
        aria-valuemin={0} aria-valuemax={100}
        aria-valuenow={Math.max(0, Math.min(100, Number(goal.progress_percent)))}
        style={{ height: 15, background: 'rgba(120,120,120,.2)', borderRadius: 5, overflow: 'hidden' }}>
        <div style={{ width: Math.max(0, Math.min(100, Number(goal.progress_percent))) + '%',
          height: '100%', background: '#16806c' }} />
      </div>
      <p>{goal.progress_percent}% {pt ? 'do alvo' : 'of target'};{' '}
        {pt ? 'faltam' : 'remaining'} {money(goal.remaining_amount, lang)}.</p>
      <p>{pt ? 'Prazo' : 'Deadline'}: {goal.deadline};{' '}
        {pt ? 'meses restantes' : 'months left'}: {goal.months_remaining}.</p>
      <p>{goal.monthly_contribution_needed === null
        ? pt ? 'Prazo encerrado; aporte mensal não calculável.' : 'Deadline passed; monthly contribution unavailable.'
        : (pt ? 'Aporte mensal projetado: ' : 'Projected monthly contribution: ') +
          money(goal.monthly_contribution_needed, lang)}</p>
      <button type="button" className="secondary" disabled={busy}
        onClick={() => void remove(goal.id)}>{pt ? 'Excluir meta' : 'Delete goal'}</button>
    </article>)}
    <small>{pt
      ? 'Progresso = valor atual do ativo / alvo; barra limitada visualmente a 100%. Aporte usa o motor RF-26, aportes ao fim do mês e retorno anual hipotético informado. Meta não reserva dinheiro nem altera patrimônio.'
      : 'Progress = current asset value / target; bar visually capped at 100%. Contribution uses the RF-26 calculation engine, end-of-month deposits and your assumed annual return. No funds are reserved or changed.'}</small>
  </section>;
}
