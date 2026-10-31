// Standalone visual demonstration only. Never called by the production transport.
// All credentials are fictional, in memory, and reset when the page is closed.
type User = { id: string; name: string; email: string; role: string; email_verified: boolean };
type Preferences = { language: 'pt' | 'en'; theme: 'light' | 'dark'; in_app_notifications: boolean; email_notifications: boolean; push_notifications: boolean };
type Category = { key: string; name: string; color: string; kind: 'standard' | 'personal'; active: boolean };
type Account = User & { password: string; preferences: Preferences; categories: Category[] };
type Attempt = { failures: number; until: number };
type Result = { status: number; detail?: string; retryAfter?: number; body?: unknown };
const accounts = new Map<string, Account>();
const attempts = new Map<string, Attempt>();
let offset = 0;
let active: Account | null = null;
export const demoNow = () => Date.now() + offset;
export function advanceDemo() { offset += 15 * 60 * 1000; }
export function resetDemo() { offset = 0; active = null; accounts.clear(); attempts.clear(); seed(); }
function seed() {
  accounts.set('art@exemplo.com', { id: 'demo-art', name: 'Art', email: 'art@exemplo.com',
    password: 'SenhaForte123', role: 'usuario', email_verified: false, preferences: defaultPreferences(), categories: defaultCategories() });
}
function defaultPreferences(): Preferences {
  return { language: 'pt', theme: 'light', in_app_notifications: true, email_notifications: false, push_notifications: false };
}
function defaultCategories(): Category[] {
  return [
    ['moradia', 'Moradia', '#5B8FF9'], ['custos-basicos', 'Custos básicos', '#61DDAA'], ['alimentacao', 'Alimentação', '#F6BD16'], ['locomocao', 'Locomoção', '#7262FD'], ['saude', 'Saúde', '#78D3F8'], ['educacao', 'Educação', '#9661BC'], ['lazer', 'Lazer', '#F6903D'], ['investimentos', 'Investimentos', '#008685'], ['doacoes', 'Doações', '#F08BB4'],
  ].map(([key, name, color]) => ({ key: `standard:${key}`, name, color, kind: 'standard', active: true }));
}
seed();
export async function demoRequest(path: string, options?: RequestInit): Promise<Result> {
  const data = options?.body ? JSON.parse(String(options.body)) : {};
  const email = String(data.email || '').trim().toLowerCase();
  const password = String(data.password || '');
  if (path === '/register' || path === '/login') {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || password.length < 8 || password.length > 128 ||
      (path === '/register' && (!String(data.name || '').trim() || String(data.name).length > 100)))
      return { status: 422, detail: 'invalid_input' };
  }
  if (path === '/register') {
    if (accounts.has(email)) return { status: 409, detail: 'email_exists' };
    const account = { id: `demo-${accounts.size}`, email, password,
      name: String(data.name).trim(), role: 'usuario', email_verified: false, preferences: defaultPreferences(), categories: defaultCategories() };
    accounts.set(email, account);
    return { status: 201, body: publicUser(account) };
  }
  if (path === '/login') {
    const attempt = attempts.get(email) || { failures: 0, until: 0 };
    const now = demoNow();
    if (attempt.until > now) return { status: 429, detail: 'login_temporarily_unavailable',
      retryAfter: Math.ceil((attempt.until - now) / 1000) };
    if (attempt.until) { attempt.failures = 0; attempt.until = 0; }
    const account = accounts.get(email);
    if (!account || account.password !== password) {
      attempt.failures += 1;
      if (attempt.failures >= 5) attempt.until = now + 900_000;
      attempts.set(email, attempt);
      return attempt.until ? { status: 429, detail: 'login_temporarily_unavailable', retryAfter: 900 }
        : { status: 401, detail: 'invalid_credentials' };
    }
    attempts.delete(email); active = account;
    return { status: 200, body: { access_token: 'fictional-demo-token', expires_in: 900 } };
  }
  if (path === '/email-confirmation') return active ? { status: 204 } : { status: 401, detail: 'invalid_session' };
  if (path === '/email-confirmation/confirm') {
    if (!active) return { status: 401, detail: 'invalid_session' };
    active.email_verified = true;
    return { status: 200, body: { email_verified: true } };
  }
  if (path === '/me') return active ? { status: 200, body: publicUser(active) }
    : { status: 401, detail: 'invalid_session' };
  if (path === '/profile') {
    if (!active) return { status: 401, detail: 'invalid_session' };
    if (options?.method === 'PATCH') {
      if (data.name) active.name = String(data.name).trim();
      if (data.email && data.email !== active.email) {
        accounts.delete(active.email); active.email = String(data.email).trim().toLowerCase(); accounts.set(active.email, active);
      }
    }
    return { status: 200, body: { user: publicUser(active), pending_email: null, preferences: active.preferences } };
  }
  if (path === '/profile/preferences') {
    if (!active) return { status: 401, detail: 'invalid_session' };
    active.preferences = { ...active.preferences, ...data };
    return { status: 200, body: active.preferences };
  }
  if (path === '/categories') {
    if (!active) return { status: 401, detail: 'invalid_session' };
    if (options?.method === 'POST') {
      if (!active.email_verified) return { status: 403, detail: 'email_not_verified' };
      const name = String(data.name || '').trim();
      if (!name || active.categories.some(item => item.name.toLowerCase() === name.toLowerCase())) return { status: 409, detail: 'category_exists' };
      const category: Category = { key: `personal:${active.categories.length}`, name, color: String(data.color || '#173F35').toUpperCase(), kind: 'personal', active: true };
      active.categories.push(category);
      return { status: 201, body: category };
    }
    return { status: 200, body: active.categories };
  }
  if (path.startsWith('/categories/standard/')) {
    if (!active) return { status: 401, detail: 'invalid_session' };
    if (!active.email_verified) return { status: 403, detail: 'email_not_verified' };
    const category = active.categories.find(item => item.key === `standard:${path.split('/').pop()}`);
    if (!category) return { status: 404, detail: 'category_not_found' };
    category.active = Boolean(data.active);
    return { status: 200, body: category };
  }
  if (path === '/sessions') return active ? { status: 200, body: [{
    id: `demo-session-${active.id}`, started_at: new Date(demoNow()).toISOString(),
    expires_at: new Date(demoNow() + 7 * 24 * 60 * 60 * 1000).toISOString(), current: true,
  }] } : { status: 401, detail: 'invalid_session' };
  if (path === '/sessions/revoke-all' || path.startsWith('/sessions/')) {
    if (!active) return { status: 401, detail: 'invalid_session' };
    active = null;
    return path === '/sessions/revoke-all' ? { status: 200, body: { revoked_sessions: 1 } } : { status: 204 };
  }
  if (path === '/logout') { active = null; return { status: 204 }; }
  if (path === '/refresh') return active ? { status: 200,
    body: { access_token: 'fictional-demo-token', expires_in: 900 } }
    : { status: 401, detail: 'invalid_session' };
  return { status: 404, detail: 'service_unavailable' };
}
function publicUser(account: Account): User {
  return { id: account.id, name: account.name, email: account.email, role: account.role, email_verified: account.email_verified };
}
