import { useCallback, useEffect, useState } from 'react';
import { api, currentCompetence, errorText, money, percent, shiftCompetence, type Lang } from './api';

type Summary = { competence: string; recurring_income: string; one_time_income: string; bonus: string; total: string; expenses: string; balance_variation: string };
type CategorySpending = { category_key: string; total: string; percentage: string };
type Category = { key: string; name: string; color: string };
type Budget = { id: string; kind: string; category_key: string | null; target: string; actual: string; percentage: string; status: string };

const monthLabel = (competence: string, lang: Lang) => {
  const [year, month] = competence.split('-').map(Number);
  const name = new Intl.DateTimeFormat(lang === 'pt' ? 'pt-BR' : 'en-US', { month: 'short', timeZone: 'UTC' })
    .format(new Date(Date.UTC(year, month - 1, 1))).replace('.', '');
  return `${name}/${String(year).slice(2)}`;
};

/** Visão geral: resumo do mês (SPEC-006), painel por período (SPEC-022) e orçamento (SPEC-021). */
export function Overview({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [competence, setCompetence] = useState(currentCompetence);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [months, setMonths] = useState<Summary[]>([]);
  const [spending, setSpending] = useState<CategorySpending[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setError('');
    try {
      const start = shiftCompetence(competence, -5);
      const [current, series, items, cats, progress] = await Promise.all([
        api<Summary>(token, `/financial/balance-summary?competence=${competence}`),
        api<Summary[]>(token, `/financial/dashboard?start=${start}&end=${competence}`),
        api<CategorySpending[]>(token, `/financial/spending-by-category?start=${competence}&end=${competence}`),
        api<Category[]>(token, '/categories'),
        api<Budget[]>(token, `/financial/budget-progress?competence=${competence}`),
      ]);
      setSummary(current); setMonths(series); setSpending(items); setCategories(cats); setBudgets(progress);
    } catch (cause) { setError(errorText(cause, lang)); }
  }, [token, competence, lang]);

  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    const refresh = () => void load();
    window.addEventListener('finnova-financial-changed', refresh);
    return () => window.removeEventListener('finnova-financial-changed', refresh);
  }, [load]);

  // Gastos do mês por categoria (pizza de RF-16), agregados no backend (SPEC-022).
  const slices = spending.map(item => [item.category_key, Number(item.total), item.percentage] as const);
  const totalSlices = slices.reduce((sum, [, value]) => sum + value, 0);
  const category = (key: string) => categories.find(item => item.key === key);
  let angle = 0;
  const arcs = slices.map(([key, value, share]) => {
    const start = angle; angle += value / (totalSlices || 1) * Math.PI * 2;
    const large = angle - start > Math.PI ? 1 : 0;
    const point = (a: number) => `${80 + 70 * Math.sin(a)},${80 - 70 * Math.cos(a)}`;
    const d = slices.length === 1 ? 'M80,10 A70,70 0 1 1 79.99,10 Z' : `M80,80 L${point(start)} A70,70 0 ${large} 1 ${point(angle)} Z`;
    return { key, value, share, d, color: category(key)?.color ?? '#8a9a90' };
  });
  const peak = Math.max(1, ...months.flatMap(item => [Number(item.total), Number(item.expenses)]));

  return <div className="stack">
    <section className="profile" aria-labelledby="overview-title">
      <div className="section-heading">
        <h3 id="overview-title">{pt ? 'Resumo do mês' : 'Monthly summary'}</h3>
        <label className="inline-field">{pt ? 'Competência' : 'Month'}
          <input type="month" value={competence} onChange={event => event.target.value && setCompetence(event.target.value)} />
        </label>
      </div>
      {error && <p role="alert" className="error">{error}</p>}
      {summary && <div className="kpis">
        <div className="kpi"><span>{pt ? 'Receitas' : 'Income'}</span><strong className="positive">{money(summary.total, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Despesas' : 'Expenses'}</span><strong className="negative">{money(summary.expenses, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Saldo do mês' : 'Net for the month'}</span><strong className={Number(summary.balance_variation) >= 0 ? 'positive' : 'negative'}>{money(summary.balance_variation, lang)}</strong></div>
        <div className="kpi"><span>{pt ? 'Taxa de poupança' : 'Savings rate'}</span><strong>{Number(summary.total) > 0 ? percent(Number(summary.balance_variation) / Number(summary.total) * 100, lang, 1) : '—'}</strong></div>
      </div>}
      {summary && <p className="hint">{pt ? 'Receitas' : 'Income'}: {pt ? 'recorrentes' : 'recurring'} {money(summary.recurring_income, lang)} · {pt ? 'pontuais' : 'one-time'} {money(summary.one_time_income, lang)} · {pt ? 'bônus/PLR' : 'bonus'} {money(summary.bonus, lang)}</p>}
    </section>

    <div className="grid-2">
      <section className="profile" aria-labelledby="dashboard-title">
        <h3 id="dashboard-title">{pt ? 'Receitas x despesas (6 meses)' : 'Income vs expenses (6 months)'}</h3>
        {months.length === 0 ? <p>{pt ? 'Sem lançamentos no período.' : 'No entries in this period.'}</p> : <>
          <svg viewBox="0 0 360 200" className="chart" role="img" aria-label={pt ? 'Gráfico de barras com receitas e despesas por mês' : 'Bar chart of income and expenses per month'}>
            {months.map((item, index) => {
              const x = 20 + index * 56; const h1 = Number(item.total) / peak * 150; const h2 = Number(item.expenses) / peak * 150;
              return <g key={item.competence}>
                <rect x={x} y={170 - h1} width="20" height={h1} rx="3" className="bar-income"><title>{money(item.total, lang)}</title></rect>
                <rect x={x + 22} y={170 - h2} width="20" height={h2} rx="3" className="bar-expense"><title>{money(item.expenses, lang)}</title></rect>
                <text x={x + 21} y="188" textAnchor="middle" fontSize="10" fill={Number(item.expenses) > Number(item.total) ? '#a02220' : 'currentColor'} fontWeight={Number(item.expenses) > Number(item.total) ? 700 : 400}>{monthLabel(item.competence, lang)}</text>
              </g>;
            })}
          </svg>
          <p className="legend"><span className="dot income" />{pt ? 'Receitas' : 'Income'} <span className="dot expense" />{pt ? 'Despesas' : 'Expenses'}</p>
          <div className="table-wrap" tabIndex={0}><table>
            <caption>{pt ? 'Valores por mês' : 'Values per month'}</caption>
            <thead><tr><th>{pt ? 'Mês' : 'Month'}</th><th>{pt ? 'Receitas' : 'Income'}</th><th>{pt ? 'Despesas' : 'Expenses'}</th><th>{pt ? 'Saldo' : 'Net'}</th></tr></thead>
            <tbody>{months.map(item => {
              const negative = Number(item.expenses) > Number(item.total);
              return <tr key={item.competence} className={negative ? 'negative-month' : undefined}><th scope="row">{monthLabel(item.competence, lang)}</th><td>{money(item.total, lang)}</td><td>{money(item.expenses, lang)}</td><td>{money(item.balance_variation, lang)}{negative && <span className="sr-only">{pt ? ' (despesas acima das receitas)' : ' (expenses above income)'}</span>}</td></tr>;
            })}</tbody>
          </table></div>
          {months.some(item => Number(item.expenses) > Number(item.total)) && <p className="hint">{pt ? 'Meses em vermelho tiveram despesas acima das receitas.' : 'Months in red had expenses above income.'}</p>}
        </>}
      </section>

      <section className="profile" aria-labelledby="categories-chart-title">
        <h3 id="categories-chart-title">{pt ? 'Gastos por categoria' : 'Spending by category'}</h3>
        {slices.length === 0 ? <p>{pt ? 'Nenhuma despesa nesta competência.' : 'No expenses this month.'}</p> : <div className="pie">
          <svg viewBox="0 0 160 160" role="img" aria-label={pt ? 'Gráfico de pizza dos gastos por categoria' : 'Pie chart of spending by category'}>
            {arcs.map(arc => <path key={arc.key} d={arc.d} fill={arc.color} stroke="#fff" strokeWidth="1"><title>{category(arc.key)?.name ?? arc.key}: {money(arc.value, lang)}</title></path>)}
          </svg>
          <ul className="legend-list">{arcs.map(arc => <li key={arc.key}><span className="dot" style={{ background: arc.color }} />{category(arc.key)?.name ?? arc.key}<b>{money(arc.value, lang)}</b><small>{percent(arc.share, lang, 1)}</small></li>)}</ul>
        </div>}
      </section>
    </div>

    <section className="profile" aria-labelledby="budget-overview-title">
      <h3 id="budget-overview-title">{pt ? 'Metas de orçamento' : 'Budget goals'}</h3>
      {budgets.length === 0 ? <p>{pt ? 'Nenhuma meta definida. Crie metas na aba Planejamento.' : 'No goals yet. Create them in the Planning tab.'}</p> :
        <ul className="progress-list">{budgets.map(goal => <li key={goal.id}>
          <div><strong>{goal.kind === 'expense_total' ? (pt ? 'Gasto total' : 'Total spending') : goal.kind === 'income_total' ? (pt ? 'Renda total' : 'Total income') : category(goal.category_key ?? '')?.name ?? goal.category_key}</strong>
            <span>{money(goal.actual, lang)} / {money(goal.target, lang)}</span></div>
          <progress max={100} value={Math.min(100, Number(goal.percentage))} aria-label={percent(goal.percentage, lang, 0)} className={goal.status} />
          <small>{percent(goal.percentage, lang, 0)} · {goal.status === 'exceeded' ? (pt ? 'excedida' : 'exceeded') : goal.status === 'reached' ? (pt ? 'meta de renda atingida' : 'income goal reached') : goal.status === 'below_target' ? (pt ? 'renda abaixo da meta' : 'income below target') : goal.status === 'alert' ? (pt ? 'perto do limite' : 'near the limit') : goal.status === 'attention' ? (pt ? 'atenção' : 'attention') : (pt ? 'dentro da meta' : 'on track')}</small>
        </li>)}</ul>}
    </section>
  </div>;
}
