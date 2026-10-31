import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, currentCompetence, errorText, money, percent, type Lang } from './api';

type Category = { key: string; name: string; active: boolean };
type Budget = { id: string; kind: string; category_key: string | null; target: string; alert_threshold: string; actual: string; percentage: string; status: string };
type Target = { monthly_contribution_needed: string; feasible: boolean; warning: string | null };
type Card = { id: string; name: string };
type Invoice = { competence: string; invoice_total: string; credit_limit: string; available_limit: string; near_limit: boolean; due_day: number };

/** Metas de orçamento (SPEC-021) e aporte para objetivo (SPEC-024). */
export function Planning({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [categories, setCategories] = useState<Category[]>([]);
  const [goals, setGoals] = useState<Budget[]>([]);
  const [goalKind, setGoalKind] = useState('expense_total');
  const [target, setTarget] = useState<Target | null>(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    try {
      const [cats, progress] = await Promise.all([
        api<Category[]>(token, '/categories'),
        api<Budget[]>(token, `/financial/budget-progress?competence=${currentCompetence()}`),
      ]);
      setCategories(cats.filter(item => item.active)); setGoals(progress);
    } catch (cause) { setError(errorText(cause, lang)); }
  }, [token, lang]);
  useEffect(() => { void load(); }, [load]);

  async function saveGoal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget; const data = new FormData(form);
    setError(''); setStatus('');
    try {
      await api(token, '/financial/budget-goals', { method: 'PUT', body: JSON.stringify({
        kind: goalKind, category_key: goalKind === 'category_expense' ? data.get('goal-category') : null,
        target: data.get('goal-target'), alert_threshold: data.get('goal-alert'),
      }) });
      form.reset(); setStatus(pt ? 'Meta salva.' : 'Goal saved.'); await load();
    } catch (cause) { setError(errorText(cause, lang)); }
  }

  async function computeTarget(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setError('');
    try {
      setTarget(await api<Target>(token, '/financial/target-contributions', { method: 'POST', body: JSON.stringify({
        target_amount: data.get('tc-target'), initial_amount: data.get('tc-initial') || '0',
        annual_rate: data.get('tc-rate'), term_months: Number(data.get('tc-term')),
        available_monthly_amount: data.get('tc-available') || null,
      }) }));
    } catch (cause) { setError(errorText(cause, lang)); }
  }

  const goalName = (goal: Budget) => goal.kind === 'expense_total' ? (pt ? 'Gasto total do mês' : 'Total monthly spending')
    : goal.kind === 'income_total' ? (pt ? 'Renda total do mês' : 'Total monthly income')
      : `${pt ? 'Categoria' : 'Category'}: ${categories.find(item => item.key === goal.category_key)?.name ?? goal.category_key}`;

  return <div className="stack">
    {error && <p className="error" role="alert">{error}</p>}
    <div className="grid-2">
      <section className="profile" aria-labelledby="budget-title">
        <h3 id="budget-title">{pt ? 'Metas de orçamento' : 'Budget goals'}</h3>
        <form onSubmit={saveGoal}>
          <div className="field"><label htmlFor="goal-kind">{pt ? 'Tipo de meta' : 'Goal type'}</label>
            <select id="goal-kind" value={goalKind} onChange={event => setGoalKind(event.target.value)}>
              <option value="expense_total">{pt ? 'Limite de gasto total' : 'Total spending limit'}</option>
              <option value="category_expense">{pt ? 'Limite por categoria' : 'Category limit'}</option>
              <option value="income_total">{pt ? 'Meta de renda' : 'Income target'}</option>
            </select></div>
          {goalKind === 'category_expense' && <div className="field"><label htmlFor="goal-category">{pt ? 'Categoria' : 'Category'}</label>
            <select id="goal-category" name="goal-category" required>{categories.map(item => <option key={item.key} value={item.key}>{item.name}</option>)}</select></div>}
          <div className="field"><label htmlFor="goal-target">{pt ? 'Valor mensal (R$)' : 'Monthly amount (BRL)'}</label><input id="goal-target" name="goal-target" type="number" min="0.01" step="0.01" required /></div>
          <div className="field"><label htmlFor="goal-alert">{pt ? 'Alertar ao atingir (%)' : 'Alert at (%)'}</label><input id="goal-alert" name="goal-alert" type="number" min="70" max="100" defaultValue="90" required /></div>
          <button type="submit">{pt ? 'Salvar meta' : 'Save goal'}</button>
        </form>
        <p className="message" role="status" aria-live="polite">{status}</p>
        <ul className="progress-list">{goals.map(goal => <li key={goal.id}>
          <div><strong>{goalName(goal)}</strong><span>{money(goal.actual, lang)} / {money(goal.target, lang)}</span></div>
          <progress max={100} value={Math.min(100, Number(goal.percentage))} className={goal.status} aria-label={percent(goal.percentage, lang, 0)} />
          <small>{percent(goal.percentage, lang, 0)} · {({ exceeded: pt ? 'excedida' : 'exceeded', alert: pt ? 'perto do limite' : 'near the limit', attention: pt ? 'atenção' : 'attention', reached: pt ? 'meta de renda atingida' : 'income goal reached', below_target: pt ? 'renda abaixo da meta' : 'income below target' } as Record<string, string>)[goal.status] ?? (pt ? 'dentro da meta' : 'on track')}</small>
        </li>)}</ul>
      </section>

      <section className="profile" aria-labelledby="target-title">
        <h3 id="target-title">{pt ? 'Quanto investir por mês para um objetivo' : 'Monthly contribution for a goal'}</h3>
        <form onSubmit={computeTarget}>
          <div className="field"><label htmlFor="tc-target">{pt ? 'Valor do objetivo (R$)' : 'Goal amount (BRL)'}</label><input id="tc-target" name="tc-target" type="number" min="0.01" step="0.01" required /></div>
          <div className="field"><label htmlFor="tc-initial">{pt ? 'Valor que já tenho (R$)' : 'Current amount (BRL)'}</label><input id="tc-initial" name="tc-initial" type="number" min="0" step="0.01" defaultValue="0" /></div>
          <div className="field"><label htmlFor="tc-rate">{pt ? 'Rentabilidade anual esperada (%)' : 'Expected annual return (%)'}</label><input id="tc-rate" name="tc-rate" type="number" min="0" step="0.01" defaultValue="10" required /></div>
          <div className="field"><label htmlFor="tc-term">{pt ? 'Prazo (meses)' : 'Term (months)'}</label><input id="tc-term" name="tc-term" type="number" min="1" max="720" defaultValue="24" required /></div>
          <div className="field"><label htmlFor="tc-available">{pt ? 'Quanto posso guardar por mês (opcional)' : 'Monthly amount available (optional)'}</label><input id="tc-available" name="tc-available" type="number" min="0" step="0.01" /></div>
          <button type="submit">{pt ? 'Calcular' : 'Calculate'}</button>
        </form>
        {target && <div className="result" role="status">
          <p>{pt ? 'Aporte mensal necessário' : 'Monthly contribution needed'}: <strong>{money(target.monthly_contribution_needed, lang)}</strong></p>
          <p className={target.feasible ? 'positive' : 'negative'}>{target.feasible ? (pt ? 'Cabe no seu orçamento informado.' : 'Fits the amount you informed.') : (pt ? 'O aporte necessário supera o valor disponível informado.' : 'The contribution exceeds the available amount.')}</p>
          <small>{pt ? 'Projeção educativa por juros compostos, sem garantia de rentabilidade.' : 'Educational compound-interest projection, not a guarantee.'}</small>
        </div>}
      </section>
    </div>
  </div>;
}

/** Fatura e limite disponível do cartão (SPEC-020). */
export function CardInvoice({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [cards, setCards] = useState<Card[]>([]);
  const [card, setCard] = useState('');
  const [competence, setCompetence] = useState(currentCompetence);
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    void api<{ credit_cards: Card[] }>(token, '/financial/sources').then(sources => {
      setCards(sources.credit_cards); setCard(current => current || sources.credit_cards[0]?.id || '');
    }).catch(cause => setError(errorText(cause, lang)));
  }, [token, lang]);
  useEffect(() => {
    if (!card) return;
    void api<Invoice>(token, `/financial/credit-cards/${card}/invoice?competence=${competence}`)
      .then(setInvoice).catch(cause => { setInvoice(null); setError(errorText(cause, lang)); });
  }, [token, card, competence, lang]);
  return <section className="profile" aria-labelledby="invoice-title">
    <h3 id="invoice-title">{pt ? 'Fatura do cartão' : 'Card statement'}</h3>
    {cards.length === 0 ? <p>{pt ? 'Cadastre um cartão em Contas e cartões.' : 'Add a card under Accounts and cards.'}</p> : <>
      <div className="inline-fields">
        <label className="inline-field">{pt ? 'Cartão' : 'Card'}<select value={card} onChange={event => setCard(event.target.value)}>{cards.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
        <label className="inline-field">{pt ? 'Competência' : 'Month'}<input type="month" value={competence} onChange={event => event.target.value && setCompetence(event.target.value)} /></label>
      </div>
      {error && <p className="error" role="alert">{error}</p>}
      {invoice && <div className="kpis">
        <div className="kpi"><span>{pt ? 'Total da fatura' : 'Statement total'}</span><strong>{money(invoice.invoice_total, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Limite disponível' : 'Available limit'}</span><strong className={invoice.near_limit ? 'negative' : 'positive'}>{money(invoice.available_limit, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Limite total' : 'Total limit'}</span><strong>{money(invoice.credit_limit, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Vencimento' : 'Due day'}</span><strong>{pt ? 'dia' : 'day'} {invoice.due_day}</strong></div>
      </div>}
      {invoice?.near_limit && <p className="negative">{pt ? 'Atenção: limite próximo do fim.' : 'Warning: close to the credit limit.'}</p>}
    </>}
  </section>;
}
