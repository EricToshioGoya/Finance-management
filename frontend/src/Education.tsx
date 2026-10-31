import { useCallback, useEffect, useState } from 'react';

export type Article = {
  key: string; title: string; body: string;
  language: 'pt' | 'en'; fallback: boolean; version: string;
};
type Language = 'pt' | 'en';
const base = '/api/v1/education/articles';

export function ContextualHelp({
  token, lang, articleKey,
}: { token: string; lang: Language; articleKey: string }) {
  const [open, setOpen] = useState(false);
  const [article, setArticle] = useState<Article | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    if (!open) return;
    const controller = new AbortController();
    setArticle(null); setError(false);
    void fetch(base + '/' + encodeURIComponent(articleKey) + '?lang=' + lang, {
      headers: { Authorization: 'Bearer ' + token }, signal: controller.signal,
    }).then(response => {
      if (!response.ok) throw new Error('article');
      return response.json() as Promise<Article>;
    }).then(setArticle).catch(() => { if (!controller.signal.aborted) setError(true); });
    return () => controller.abort();
  }, [articleKey, lang, open, token]);
  return <span style={{ display: 'inline-block', verticalAlign: 'middle', marginInlineStart: 5 }}>
    <button type="button" className="secondary"
      aria-expanded={open} aria-label={lang === 'pt' ? 'Abrir explicação' : 'Open explanation'}
      onClick={() => setOpen(previous => !previous)}
      style={{ padding: '2px 9px', minWidth: 28 }}>?</button>
    {open && <span role="region" aria-live="polite"
      style={{ display: 'block', padding: 10, marginTop: 6, border: '1px solid #83909b',
        borderRadius: 7, maxWidth: 380 }}>
      {article ? <><strong>{article.title}</strong><p>{article.body}</p>
        {article.fallback && <small>{lang === 'pt' ? 'Tradução indisponível' :
          'Translation unavailable'}</small>}</>
        : error ? <span>{lang === 'pt' ? 'Explicação indisponível.' :
          'Explanation unavailable.'}</span>
          : <span>{lang === 'pt' ? 'Carregando explicação…' :
            'Loading explanation…'}</span>}
      <button className="secondary" type="button" onClick={() => setOpen(false)}>
        {lang === 'pt' ? 'Fechar' : 'Close'}
      </button>
    </span>}
  </span>;
}

export function EducationCenter({
  token, lang,
}: { token: string; lang: Language }) {
  const [query, setQuery] = useState('');
  const [articles, setArticles] = useState<Article[]>([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const load = useCallback(async (term: string, signal: AbortSignal) => {
    try {
      const response = await fetch(base + '?lang=' + lang + '&q=' + encodeURIComponent(term), {
        headers: { Authorization: 'Bearer ' + token }, signal,
      });
      if (!response.ok) throw new Error('fetch');
      setArticles(await response.json() as Article[]);
      setError(false);
    } catch {
      if (!signal.aborted) { setArticles([]); setError(true); }
    } finally { if (!signal.aborted) setLoading(false); }
  }, [token, lang]);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    void load(query.trim(), controller.signal);
    return () => controller.abort();
  }, [query, load]);
  const pt = lang === 'pt';
  return <section className="profile" aria-labelledby="education-center-heading">
    <h3 id="education-center-heading">{pt ? 'Central de educação financeira' : 'Financial learning center'}</h3>
    <p>{pt ? 'Verbetes educativos priorizados conforme seu perfil, sem recomendação de investimentos.' :
      'Educational articles ordered for your profile, not investment advice.'}</p>
    <label>{pt ? 'Buscar um conceito' : 'Search a topic'}
      <input type="search" maxLength={100} value={query}
        onChange={event => setQuery(event.target.value)}
        placeholder={pt ? 'Ex.: CDI, Sharpe, diversificação' : 'E.g. CDI, Sharpe, diversification'} />
    </label>
    {loading && <p role="status">{pt ? 'Buscando…' : 'Searching…'}</p>}
    {error && <p role="alert">{pt ? 'Não foi possível carregar os verbetes.' :
      'Could not load articles.'}</p>}
    {!loading && !error && articles.length === 0 && <p role="status">
      {pt ? 'Nenhum verbete encontrado. Tente outra palavra.' :
        'No matching article. Try another term.'}
    </p>}
    {!loading && !error && <div>{articles.map(article => <article key={article.key}
      style={{ paddingBlock: 8, borderBottom: '1px solid #83909b' }}>
      <h4>{article.title}</h4>
      <p>{article.body}</p>
      {article.fallback && <small role="status">{pt ? 'Idioma alternativo utilizado' :
        'Fallback language used'}</small>}
    </article>)}</div>}
  </section>;
}
