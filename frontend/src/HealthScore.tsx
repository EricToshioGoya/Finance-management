import { useCallback, useEffect, useState } from 'react';

type FactorKey = 'spending' | 'reserve' | 'debt' | 'goals';
type Classification = 'critical' | 'attention' | 'healthy' | 'excellent';
type Score = {
  competence: string;
  score: string;
  classification: Classification;
  factors: { key: FactorKey; score: string; suggestion: string }[];
  history: { competence: string; score: string }[];
  rule_version: string;
  educational: boolean;
};
const labels: Record<Classification, { pt: string; en: string }> = {
  critical: { pt: 'Crítico', en: 'Critical' },
  attention: { pt: 'Atenção', en: 'Attention' },
  healthy: { pt: 'Saudável', en: 'Healthy' },
  excellent: { pt: 'Excelente', en: 'Excellent' },
};
const factors: Record<FactorKey, { pt: string; en: string; ptTip: string; enTip: string }> = {
  spending: {
    pt: 'Relação gastos / renda', en: 'Expenses / income',
    ptTip: 'Reveja suas despesas para preservar uma parcela maior da renda.',
    enTip: 'Review your expenses to keep more of your income.',
  },
  reserve: {
    pt: 'Reserva de emergência', en: 'Emergency reserve',
    ptTip: 'Considere construir uma reserva para gastos inesperados.',
    enTip: 'Consider building a reserve for unexpected expenses.',
  },
  debt: {
    pt: 'Comprometimento com dívidas', en: 'Debt burden',
    ptTip: 'Reveja o peso das faturas e dívidas na sua renda.',
    enTip: 'Review how much debt and card bills weigh on your income.',
  },
  goals: {
    pt: 'Aderência às metas', en: 'Goal adherence',
    ptTip: 'Reavalie as metas e compare-as com o orçamento realizado.',
    enTip: 'Review your targets against your actual budget.',
  },
};
function monthLabel(iso: string, lang: 'pt' | 'en') {
  const [year, month] = iso.split('-').map(Number);
  if (!year || !month) return iso;
  return new Intl.DateTimeFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
    month: 'short', year: '2-digit', timeZone: 'UTC',
  }).format(new Date(Date.UTC(year, month - 1, 1)));
}
const clamp = (number: number) => Math.max(0, Math.min(100, number));

export function HealthScore({ token, lang }: { token: string; lang: 'pt' | 'en' }) {
  const pt = lang === 'pt';
  const [score, setScore] = useState<Score | null>(null);
  const [month, setMonth] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<'income' | 'rule' | 'other' | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const reload = useCallback(async () => {
    try {
      const params = month ? '?competence=' + encodeURIComponent(month + '-01') : '';
      const response = await fetch('/api/v1/auth/financial/health-score' + params, {
        headers: { Authorization: 'Bearer ' + token },
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({})) as { detail?: string };
        if (payload.detail === 'health_score_income_unavailable') throw new Error('income');
        if (payload.detail === 'health_score_rule_unavailable') throw new Error('rule');
        throw new Error('other');
      }
      const payload = await response.json() as Score;
      setScore(payload);
      setError(null);
    } catch (cause) {
      setScore(null);
      const reason = cause instanceof Error && ['income', 'rule'].includes(cause.message)
        ? cause.message as 'income' | 'rule' : 'other';
      setError(reason);
    } finally {
      setLoading(false);
    }
  }, [token, month]);

  useEffect(() => { setLoading(true); void reload(); }, [reload, refreshKey]);
  useEffect(() => {
    const refresh = () => {
      if (document.visibilityState === 'visible') setRefreshKey(previous => previous + 1);
    };
    window.addEventListener('focus', refresh);
    document.addEventListener('visibilitychange', refresh);
    window.addEventListener('finnova-financial-changed', refresh);
    return () => {
      window.removeEventListener('focus', refresh);
      document.removeEventListener('visibilitychange', refresh);
      window.removeEventListener('finnova-financial-changed', refresh);
    };
  }, []);

  const scoreNumber = score ? clamp(Number(score.score)) : 0;
  const history = score?.history ?? [];
  const points = history.map((row, index) => ({
    label: monthLabel(row.competence, lang),
    value: clamp(Number(row.score)),
    x: history.length === 1 ? 50 : 5 + index * 90 / (history.length - 1),
  }));
  const polyline = points.map(point => `${point.x},${95 - point.value * .9}`).join(' ');

  return <section className="profile" aria-labelledby="health-score-title">
    <h3 id="health-score-title">{pt ? 'Score de saúde financeira' : 'Financial health score'}</h3>
    <p>{pt
      ? 'Pontuação educativa de 0 a 100, baseada em renda, gastos, reserva, dívidas e metas. Não constitui recomendação financeira.'
      : 'Educational score from 0 to 100 based on income, spending, reserves, debt, and goals. Not financial advice.'}</p>
    <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'end' }}>
      <label>{pt ? 'Competência (opcional)' : 'Month (optional)'}
        <input type="month" value={month} onChange={event => setMonth(event.target.value)} />
      </label>
      <button className="secondary" type="button"
        onClick={() => setRefreshKey(previous => previous + 1)}>
        {pt ? 'Atualizar score' : 'Refresh score'}
      </button>
      {month && <button className="secondary" type="button"
        onClick={() => setMonth('')}>{pt ? 'Voltar ao atual' : 'Current month'}</button>}
    </div>
    {loading && <p role="status">{pt ? 'Calculando score…' : 'Calculating score…'}</p>}
    {!loading && error === 'income' && <p role="status">
      {pt ? 'Não há renda registrada nesta competência. O score não pode ser calculado sem dados suficientes.'
        : 'No income recorded for this month. A score cannot be calculated without sufficient data.'}
    </p>}
    {!loading && error === 'rule' && <p role="alert">
      {pt ? 'A regra de pontuação não está disponível. Nenhuma nota foi atribuída.'
        : 'The scoring rule is unavailable. No score was assigned.'}
    </p>}
    {!loading && error === 'other' && <p role="alert">
      {pt ? 'Não foi possível consultar o score. Verifique a conexão ou a sessão.'
        : 'Could not load your score. Check your connection or session.'}
    </p>}
    {score && !loading && <>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 24, alignItems: 'center' }}>
        <div style={{ display: 'grid', placeItems: 'center', width: 176, height: 176,
          borderRadius: '50%', background: `conic-gradient(#17816e ${scoreNumber}%, #b7c2cc 0)` }}>
          <div style={{ background: 'var(--surface, #fff)', color: 'var(--text, #152633)',
            display: 'grid', placeContent: 'center', borderRadius: '50%',
            width: 143, height: 143, textAlign: 'center' }}>
            <strong style={{ fontSize: 40, fontVariantNumeric: 'tabular-nums' }}>
              {Number(score.score).toFixed(1)}
            </strong>
            <span style={{ fontSize: 14 }}>/ 100</span>
          </div>
        </div>
        <div>
          <h4 style={{ marginBottom: 6 }}>{labels[score.classification][lang]}</h4>
          <p>{pt ? 'Referência' : 'Reference'}: {monthLabel(score.competence, lang)}</p>
          <p>{pt ? 'Regra aplicada' : 'Applied rule'}: {score.rule_version}</p>
        </div>
      </div>
      <h4>{pt ? 'Fatores para melhorar' : 'Factors to improve'}</h4>
      <ul>{score.factors.map(factor => <li key={factor.key}>
        <strong>{factors[factor.key][lang]}: {Number(factor.score).toFixed(1)} / 100.</strong>
        {' '}{pt ? factors[factor.key].ptTip : factors[factor.key].enTip}
      </li>)}</ul>
      <h4>{pt ? 'Evolução mensal' : 'Monthly trend'}</h4>
      {history.length === 0 ? <p>{pt ? 'Sem histórico ainda.' : 'No history yet.'}</p> :
        <div>
          <svg viewBox="0 0 100 105" preserveAspectRatio="none"
            role="img" aria-label={pt ? 'Gráfico de linha da evolução mensal do score' :
              'Line chart of monthly health score'} style={{ width: '100%', height: 170 }}>
            {[0, 25, 50, 75, 100].map(value => <line key={value}
              x1="0" x2="100" y1={95 - value * .9} y2={95 - value * .9}
              stroke="currentColor" strokeOpacity=".13" strokeWidth=".4" />)}
            <polyline fill="none" stroke="#16806c" strokeWidth="1.5"
              vectorEffect="non-scaling-stroke" points={polyline} />
            {points.map((point, index) => <circle key={history[index].competence}
              cx={point.x} cy={95 - point.value * .9} r="1.5"
              fill="#16806c" vectorEffect="non-scaling-stroke" />)}
          </svg>
          <div className="indicator-table-wrap">
            <table><caption>{pt ? 'Histórico do score por competência' : 'Health score history by month'}</caption>
              <thead><tr><th>{pt ? 'Mês' : 'Month'}</th><th>{pt ? 'Nota' : 'Score'}</th></tr></thead>
              <tbody>{history.map(item => <tr key={item.competence}>
                <th scope="row">{monthLabel(item.competence, lang)}</th><td>{item.score} / 100</td>
              </tr>)}</tbody>
            </table>
          </div>
        </div>}
      <small>{pt ? 'A atualização recalcula o mês selecionado com os lançamentos atuais desse período; o histórico é mensal e não representa recomendações de investimento.'
        : 'Refreshing recalculates the selected month from its financial entries; history is monthly and does not represent investment advice.'}</small>
    </>}
  </section>;
}
