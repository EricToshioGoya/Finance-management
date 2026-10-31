import { useCallback, useEffect, useState } from 'react';
import { api, errorText, percent, shortDate, type Lang } from './api';

type Benchmark = { enabled: boolean; available: boolean; reason: string | null; profile: string | null; competence: string | null; minimum_group_size: number; my_score: string | null; group_average_score: string | null; group_median_score: string | null; my_savings_rate: string | null; group_average_savings_rate: string | null; group_median_savings_rate: string | null };
type Achievement = { code: string; title: string; description: string; unlocked: boolean; unlocked_at: string | null; progress_percent: string };
type Tour = { status: string; show: boolean; step: number; variant: 'didactic' | 'concise'; profile: string | null; steps: { key: string; tab: string; done: boolean }[] };

/** Comparação anônima do score com o grupo do mesmo perfil (SPEC-050). */
export function ScoreBenchmark({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [data, setData] = useState<Benchmark | null>(null);
  const [error, setError] = useState('');
  const load = useCallback(async () => {
    try { setData(await api<Benchmark>(token, '/financial/health-score/benchmark')); } catch (cause) { setError(errorText(cause, lang)); }
  }, [token, lang]);
  useEffect(() => { void load(); }, [load]);
  async function toggle() {
    if (!data) return;
    await api(token, '/profile/privacy', { method: 'PUT', body: JSON.stringify({ score_benchmark_enabled: !data.enabled }) }).catch(() => undefined);
    await load();
  }
  const reasons: Record<string, [string, string]> = {
    opted_out: ['Comparação desativada nas suas configurações de privacidade.', 'Comparison disabled in your privacy settings.'],
    no_profile: ['Responda o quiz de perfil para comparar com pessoas do mesmo perfil.', 'Answer the profile quiz to compare with people of the same profile.'],
    no_score: ['Calcule seu score para ver a comparação.', 'Calculate your score to see the comparison.'],
    insufficient_group: ['Ainda não há pessoas suficientes do seu perfil para uma comparação anônima.', 'Not enough people with your profile yet for an anonymous comparison.'],
  };
  return <section className="profile" aria-labelledby="benchmark-title">
    <h3 id="benchmark-title">{pt ? 'Comparação com pessoas do seu perfil' : 'Comparison with your profile group'}</h3>
    {error && <p className="error" role="alert">{error}</p>}
    {data && <>
      {data.available ? <div className="table-wrap" tabIndex={0}><table>
        <caption>{pt ? `Médias agregadas e anônimas de um grupo com no mínimo ${data.minimum_group_size} pessoas · ${data.competence}` : `Anonymous aggregated values from a group of at least ${data.minimum_group_size} people · ${data.competence}`}</caption>
        <thead><tr><th>{pt ? 'Indicador' : 'Metric'}</th><th className="num">{pt ? 'Você' : 'You'}</th><th className="num">{pt ? 'Média do grupo' : 'Group average'}</th><th className="num">{pt ? 'Mediana' : 'Median'}</th></tr></thead>
        <tbody>
          <tr><th scope="row">Score</th><td className="num">{data.my_score}</td><td className="num">{data.group_average_score}</td><td className="num">{data.group_median_score}</td></tr>
          <tr><th scope="row">{pt ? '% da renda poupada' : '% of income saved'}</th><td className="num">{data.my_savings_rate ? percent(data.my_savings_rate, lang, 1) : '—'}</td><td className="num">{data.group_average_savings_rate ? percent(data.group_average_savings_rate, lang, 1) : '—'}</td><td className="num">{data.group_median_savings_rate ? percent(data.group_median_savings_rate, lang, 1) : '—'}</td></tr>
        </tbody>
      </table></div> : <p className="hint">{data.reason ? reasons[data.reason][pt ? 0 : 1] : ''}</p>}
      <label className="check"><input type="checkbox" checked={data.enabled} onChange={() => void toggle()} />{pt ? 'Participar da comparação anônima (desativar não afeta seu score)' : 'Join the anonymous comparison (turning off does not affect your score)'}</label>
    </>}
  </section>;
}

/** Conquistas cosméticas: obtidas e próximas (SPEC-051). */
export function Achievements({ token, lang }: { token: string; lang: Lang }) {
  const pt = lang === 'pt';
  const [items, setItems] = useState<Achievement[]>([]);
  useEffect(() => { void api<Achievement[]>(token, '/financial/achievements').then(setItems).catch(() => setItems([])); }, [token]);
  return <section className="profile" aria-labelledby="achievements-title">
    <h3 id="achievements-title">{pt ? 'Conquistas' : 'Achievements'}</h3>
    <p className="hint">{pt ? 'Conquistas são apenas motivacionais: não alteram cálculos, score nem permissões.' : 'Achievements are motivational only: they never change calculations, score or permissions.'}</p>
    <ul className="achievement-list">{items.map(item => <li key={item.code} className={item.unlocked ? 'unlocked' : ''}>
      <span className="medal" aria-hidden="true">{item.unlocked ? '★' : '☆'}</span>
      <div><strong>{item.title}</strong><small>{item.description}</small>
        {item.unlocked ? <small className="positive">{pt ? 'Obtida em' : 'Unlocked on'} {item.unlocked_at && shortDate(item.unlocked_at, lang)}</small>
          : <progress max={100} value={Number(item.progress_percent)} aria-label={`${item.title}: ${percent(item.progress_percent, lang, 0)}`} />}
      </div>
    </li>)}</ul>
  </section>;
}

const stepText: Record<string, { pt: [string, string]; en: [string, string] }> = {
  first_income: { pt: ['Cadastre sua primeira receita', 'Na aba Lançamentos, escolha "Receita recorrente" para o salário ou "Receita pontual" para um valor avulso.'], en: ['Add your first income', 'In Transactions, choose "Recurring income" for salary or "One-time income" for occasional amounts.'] },
  first_expense: { pt: ['Registre sua primeira despesa', 'Ainda em Lançamentos, informe valor, data, categoria e a conta ou o cartão usado.'], en: ['Record your first expense', 'In Transactions, enter amount, date, category and the account or card used.'] },
  investor_quiz: { pt: ['Descubra seu perfil de investidor', 'Em Minha conta, responda 5 perguntas rápidas. O resultado adapta as orientações do simulador.'], en: ['Find your investor profile', 'In My account, answer 5 quick questions. The result tailors the simulator guidance.'] },
  simulator: { pt: ['Faça sua primeira simulação', 'Em Investimentos, use a calculadora de juros compostos e salve uma simulação. Simular nunca altera seu saldo real.'], en: ['Run your first simulation', 'In Investments, use the compound interest calculator and save a simulation. Simulating never changes your real balance.'] },
};

/** Tour guiado do primeiro acesso, opcional e reabrível (SPEC-052). */
export function OnboardingTour({ token, lang, onNavigate, version }: { token: string; lang: Lang; onNavigate: (tab: string) => void; version: number }) {
  const pt = lang === 'pt';
  const [tour, setTour] = useState<Tour | null>(null);
  const load = useCallback(async () => { setTour(await api<Tour>(token, '/profile/tour').catch(() => null)); }, [token]);
  useEffect(() => { void load(); }, [load, version]);
  const act = async (action: string, step?: number) => setTour(await api<Tour>(token, '/profile/tour', { method: 'PUT', body: JSON.stringify(step === undefined ? { action } : { action, step }) }).catch(() => tour));
  if (!tour?.show) return null;
  const current = tour.steps[Math.min(tour.step, tour.steps.length - 1)];
  const [title, body] = stepText[current.key][pt ? 'pt' : 'en'];
  const concise = tour.variant === 'concise';
  return <section className="profile tour" aria-labelledby="tour-title">
    <div className="section-heading"><h3 id="tour-title">{pt ? 'Primeiros passos' : 'Getting started'} · {tour.step + 1}/4</h3>
      <button type="button" className="secondary" onClick={() => void act('skip')}>{pt ? 'Pular tour' : 'Skip tour'}</button></div>
    {concise ? <p className="hint">{pt ? 'Você já tem experiência: veja o essencial e vá direto às funções avançadas (Investimentos, Impostos e Patrimônio).' : 'You are experienced: here is the essentials, then jump to advanced features (Investments, Taxes and Net worth).'}</p>
      : !tour.profile && <p className="hint">{pt ? 'Vamos com calma: siga os passos abaixo. Você pode pular a qualquer momento e reabrir pela aba Aprender.' : 'Let’s take it slowly: follow the steps below. You can skip anytime and reopen it from the Learn tab.'}</p>}
    <ol className="tour-steps">{tour.steps.map((step, index) => <li key={step.key} className={index === tour.step ? 'current' : step.done ? 'done' : ''}>{stepText[step.key][pt ? 'pt' : 'en'][0]}{step.done && ' ✓'}</li>)}</ol>
    <p><strong>{title}.</strong> {concise ? '' : body}</p>
    <div className="actions">
      <button type="button" onClick={() => onNavigate(current.tab)}>{pt ? 'Ir para esta etapa' : 'Go to this step'}</button>
      {tour.step < 3 ? <button type="button" className="secondary" onClick={() => void act('advance')}>{pt ? 'Próxima' : 'Next'}</button>
        : <button type="button" className="secondary" onClick={() => void act('complete')}>{pt ? 'Concluir' : 'Finish'}</button>}
    </div>
  </section>;
}

/** Botão de ajuda para reabrir o tour (R05). */
export function ReopenTour({ token, lang, onReopen }: { token: string; lang: Lang; onReopen: () => void }) {
  const pt = lang === 'pt';
  return <section className="profile" aria-labelledby="help-title">
    <h3 id="help-title">{pt ? 'Ajuda' : 'Help'}</h3>
    <p className="hint">{pt ? 'Quer rever o passo a passo inicial?' : 'Want to see the getting-started guide again?'}</p>
    <button type="button" onClick={() => void api(token, '/profile/tour', { method: 'PUT', body: JSON.stringify({ action: 'reopen' }) }).then(onReopen)}>{pt ? 'Reabrir tour guiado' : 'Reopen guided tour'}</button>
  </section>;
}
