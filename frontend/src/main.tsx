import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import { translations, type Language, type Message } from './i18n';
import { NetWorthHistory } from './NetWorthHistory';
import { NetWorthHeatmap } from './NetWorthHeatmap';
import { InvestmentAllocation } from './InvestmentAllocation';
import { FinancialStress } from './FinancialStress';
import { Financing } from './Financing';
import { ExternalIntegrations } from './ExternalIntegrations';
import { ConfirmFinancing } from './ConfirmFinancing';
import { FinancingComparison } from './FinancingComparison';
import { EducationCenter } from './Education';
import { HealthScore } from './HealthScore';
import { NamedAssetGoals } from './NamedAssetGoals';
import { Overview } from './Overview';
import { Transactions } from './Transactions';
import { CardInvoice, Planning } from './Planning';
import { Investments } from './Investments';
import { Sharing } from './Sharing';
import { PensionComparison, RetirementPlanner, Taxes } from './PlanningTax';
import { Achievements, OnboardingTour, ReopenTour, ScoreBenchmark } from './Engagement';
import { AdminEngagement, AdminProfileDistribution, NetWorthItems, Notifications, Watchlist } from './Extras';
import { money } from './api';
import './style.css';
import { demoRequest, demoNow, advanceDemo, resetDemo } from './demo';

type InvestorProfile = 'conservador' | 'moderado' | 'arrojado';
type User = { id: string; name: string; email: string; role: string; email_verified: boolean; investor_profile: InvestorProfile | null };
type QuizQuestion = { id: string; prompt: string; options: string[] };
type Session = { access_token: string; expires_in: number };
type ManagedSession = { id: string; started_at: string; expires_at: string; current: boolean };
type Preferences = { language: Language; theme: 'light' | 'dark'; in_app_notifications: boolean; email_notifications: boolean; push_notifications: boolean };
type Profile = { user: User; pending_email: string | null; preferences: Preferences };
type Category = { key: string; name: string; color: string; kind: 'standard' | 'personal'; active: boolean };
type Account = { id: string; name: string; account_type: string; initial_balance: string };
type CreditCard = { id: string; name: string; credit_limit: string; closing_day: number; due_day: number };
type FinancialSources = { accounts: Account[]; credit_cards: CreditCard[] };
type AdminUser = { id: string; name: string; email: string; created_at: string; investor_profile: InvestorProfile | null; status: 'active' };
type AdminUsersPage = { items: AdminUser[]; page: number; page_size: number; total: number };
type PublicCompany = { id: string; ticker: string; cnpj: string; legal_name: string; sector: string };
type OfficialDocument = { id: string; company_id: string; document_type: 'DFP' | 'ITR' | 'FRE' | 'IPE'; subject: string; reference_period: string; delivered_at: string; status: 'active' | 'restated' | 'replaced'; official_url: string; link_status: 'unchecked' | 'available' | 'broken'; last_checked_at: string | null };
type FinancialIndicator = { id: string; company_id: string; metric: 'net_revenue' | 'net_income' | 'equity'; period_kind: 'annual' | 'quarterly'; reference_period: string; reference_date: string; value: string; unit: 'BRL_THOUSANDS'; source_name: string; source_url: string; status: 'active' | 'restated'; published_at: string; synced_at: string; effective: boolean };
type MarketQuote = { ticker: string; asset_kind: 'stock' | 'fii'; price: string; daily_change_percent: string; referenced_at: string; fresh_until: string; source_name: string; catalogue_type: 'local_reference'; history: { quoted_on: string; close_price: string }[] };
type Tab = 'overview' | 'transactions' | 'sharing' | 'planning' | 'investments' | 'taxes' | 'patrimony' | 'financing' | 'companies' | 'learn' | 'account' | 'admin';
const prefix = '/api/v1/auth';
const visualPreview = document.documentElement.dataset.preview === 'visual';
const interactivePreview = document.documentElement.dataset.preview === 'interactive';
const nowMs = () => interactivePreview ? demoNow() : Date.now();
const hashConfirmationToken = () => {
  const [, query = ''] = window.location.hash.split('?');
  return new URLSearchParams(query).get('token') || '';
};

function preferredLanguage(): Language {
  try { return localStorage.getItem('finnova-language') === 'en' ? 'en' : 'pt'; }
  catch { return 'pt'; }
}

class ApiError extends Error {
  constructor(code: string, readonly retryAfter?: number, readonly manualEntryPermitted = false) { super(code); }
}
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  if (interactivePreview) {
    const result = await demoRequest(path, options);
    if (result.status >= 400) throw new ApiError(result.detail || 'service_unavailable', result.retryAfter);
    return result.body as T;
  }
  let response: Response;
  try { response = await fetch(path.startsWith('/api/') ? path : prefix + path, { credentials: 'same-origin', ...options }); }
  catch { throw new ApiError('network'); }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const retry = Number(response.headers.get('Retry-After'));
    throw new ApiError(typeof body.detail === 'string' ? body.detail : 'service_unavailable',
      Number.isFinite(retry) && retry > 0 ? retry : undefined, body.manual_entry_permitted === true);
  }
  if (path.startsWith('/financial/') && ['POST', 'PATCH', 'PUT', 'DELETE'].includes(options?.method?.toUpperCase() ?? '')) {
    window.dispatchEvent(new Event('finnova-financial-changed'));
  }
  return response.status === 204 ? undefined as T : response.json();
}

async function refreshSession(): Promise<Session> {
  const renew = () => request<Session>('/refresh', { method: 'POST' });
  // Coordinate cookie rotation between tabs so a legitimate simultaneous reload
  // does not look like a stolen refresh token being replayed.
  return navigator.locks ? navigator.locks.request('finnova-refresh', renew) : renew();
}

function App() {
  const [deletionReview, setDeletionReview] = useState(false);
  const [lang, setLang] = useState<Language>(preferredLanguage);
  const [mode, setMode] = useState<'login' | 'register' | 'recovery'>('login');
  const [user, setUser] = useState<User | null>(null);
  const [managedSessions, setManagedSessions] = useState<ManagedSession[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [creditCards, setCreditCards] = useState<CreditCard[]>([]);
  const [tab, setTab] = useState<Tab>('overview');
  const [watchVersion, setWatchVersion] = useState(0);
  const [tourVersion, setTourVersion] = useState(0);
  const [adminUsers, setAdminUsers] = useState<AdminUsersPage | null>(null);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [companies, setCompanies] = useState<PublicCompany[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<PublicCompany | null>(null);
  const [officialDocuments, setOfficialDocuments] = useState<OfficialDocument[]>([]);
  const [financialIndicators, setFinancialIndicators] = useState<FinancialIndicator[]>([]);
  const [marketQuote, setMarketQuote] = useState<MarketQuote | null>(null);
  const [manualMarketEntry, setManualMarketEntry] = useState(false);
  const [preferences, setPreferences] = useState<Preferences>({ language: 'pt', theme: 'light', in_app_notifications: true, email_notifications: false, push_notifications: false });
  const [pendingEmail, setPendingEmail] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(!visualPreview && !interactivePreview);
  const [message, setMessage] = useState<Message | null>(null);
  const [error, setError] = useState(false);
  const [retryAt, setRetryAt] = useState(0);
  const [confirmationToken, setConfirmationToken] = useState(hashConfirmationToken);
  const [passwordResetToken, setPasswordResetToken] = useState(
    window.location.hash.startsWith('#/redefinir-senha') ? hashConfirmationToken() : '',
  );
  const [now, setNow] = useState(nowMs);
  const access = useRef<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const heading = useRef<HTMLHeadingElement>(null);
  const t = translations[lang];

  function notify(cause: unknown) {
    const code = cause instanceof ApiError ? cause.message : 'service_unavailable';
    setMessage(code in translations.pt ? code as Message : 'service_unavailable');
    setError(true); setNow(nowMs());
    setRetryAt(cause instanceof ApiError && cause.retryAfter ? nowMs() + cause.retryAfter * 1000 : 0);
  }
  async function acceptSession(session: Session) {
    access.current = session.access_token;
    const authHeaders = { Authorization: `Bearer ${session.access_token}` };
    const [profile, currentSessions, currentCategories, sources, questions] = await Promise.all([
      request<Profile>('/profile', { headers: authHeaders }),
      request<ManagedSession[]>('/sessions', { headers: authHeaders }),
      request<Category[]>('/categories', { headers: authHeaders }),
      interactivePreview ? Promise.resolve<FinancialSources>({ accounts: [], credit_cards: [] }) : request<FinancialSources>('/financial/sources', { headers: authHeaders }),
      interactivePreview ? Promise.resolve<QuizQuestion[]>([]) : request<QuizQuestion[]>('/investor-profile/quiz', { headers: authHeaders }),
    ]);
    setUser(profile.user); setPendingEmail(profile.pending_email); setPreferences(profile.preferences);
    setLang(profile.preferences.language); setManagedSessions(currentSessions); setCategories(currentCategories);
    setAccounts(sources.accounts); setCreditCards(sources.credit_cards); setRetryAt(0);
    setQuizQuestions(questions);
    // Best-effort telemetry: it is never allowed to delay or invalidate sign-in.
    void request<void>('/usage-events', {
      method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.access_token}` },
      body: JSON.stringify({ module: 'dashboard', action: 'opened' }),
    }).catch(() => undefined);
    if (profile.user.role === 'administrador' && !interactivePreview) {
      void fetch('/api/v1/admin/users?page=1&page_size=20', {
        credentials: 'same-origin', headers: { Authorization: `Bearer ${session.access_token}` },
      }).then(async response => response.ok ? response.json() as Promise<AdminUsersPage> : null)
        .then(result => setAdminUsers(result)).catch(() => setAdminUsers(null));
    } else setAdminUsers(null);
    clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      try { await acceptSession(await refreshSession()); }
      catch (cause) { access.current = null; setUser(null); notify(cause); }
    }, Math.max(1, session.expires_in - 30) * 1000);
  }
  useEffect(() => {
    if (!retryAt) return;
    const tick = setInterval(() => setNow(nowMs()), 1000);
    return () => clearInterval(tick);
  }, [retryAt]);
  useEffect(() => {
    document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en';
    try { localStorage.setItem('finnova-language', lang); }
    catch { /* File previews and sandboxed browsers may block local storage. */ }
  }, [lang]);
  useEffect(() => { document.documentElement.dataset.theme = preferences.theme; }, [preferences.theme]);
  useEffect(() => {
    if (visualPreview || interactivePreview) return;
    let active = true;
    refreshSession()
      .then(async session => { if (active) await acceptSession(session); })
      .catch(cause => { if (active && cause.message !== 'invalid_session') notify(cause); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; clearTimeout(timer.current); };
  }, []);
  useEffect(() => { if (!loading) heading.current?.focus(); }, [user, mode, loading]);
  useEffect(() => {
    if (user && !user.email_verified && confirmationToken) void confirmEmail(confirmationToken);
  }, [user, confirmationToken]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (visualPreview) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    setBusy(true); setMessage(null); setError(false);
    try {
      const body = mode === 'recovery'
        ? { email: data.get('email') }
        : { email: data.get('email'), password: data.get('password'),
          ...(mode === 'register' ? { name: data.get('name') } : {}) };
      const result = await request<Session | User>(
        mode === 'recovery' ? '/password-recovery' : `/${mode}`,
        {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
        },
      );
      form.reset();
      if (mode === 'register') { setMode('login'); setMessage('success'); }
      else if (mode === 'recovery') { setMode('login'); setMessage('passwordRecoverySent'); }
      else await acceptSession(result as Session);
    } catch (cause) { notify(cause); }
    finally {
      const field = form.elements.namedItem('password') as HTMLInputElement | null;
      if (field) field.value = '';
      setBusy(false);
    }
  }
  async function submitPasswordReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!passwordResetToken || visualPreview) return;
    const data = new FormData(event.currentTarget);
    setBusy(true); setMessage(null); setError(false);
    try {
      await request<void>('/password-recovery/confirm', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: passwordResetToken, new_password: data.get('new-password') }),
      });
      setPasswordResetToken(''); history.replaceState(null, '', window.location.pathname);
      setMode('login'); setMessage('passwordReset');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function submitPasswordChange(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!access.current || visualPreview) return;
    const data = new FormData(event.currentTarget);
    setBusy(true); setMessage(null); setError(false);
    try {
      await request<void>('/password', {
        method: 'PATCH', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + access.current },
        body: JSON.stringify({ current_password: data.get('change-current-password'), new_password: data.get('change-new-password') }),
      });
      clearTimeout(timer.current); access.current = null; setUser(null); setManagedSessions([]);
      setMessage('passwordChanged');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function submitCategory(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!access.current || visualPreview) return;
    const data = new FormData(event.currentTarget);
    setBusy(true); setMessage(null); setError(false);
    try {
      const created = await request<Category>('/categories', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + access.current },
        body: JSON.stringify({ name: data.get('category-name'), color: data.get('category-color') }),
      });
      setCategories(current => [...current, created]); event.currentTarget.reset(); setMessage('categoryCreated');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function toggleDefaultCategory(category: Category) {
    if (!access.current || visualPreview) return;
    const key = category.key.replace('standard:', '');
    setBusy(true); setMessage(null); setError(false);
    try {
      const updated = await request<Category>(`/categories/standard/${key}`, {
        method: 'PATCH', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + access.current },
        body: JSON.stringify({ active: !category.active }),
      });
      setCategories(current => current.map(item => item.key === updated.key ? updated : item));
      setMessage(updated.active ? 'categoryShown' : 'categoryHidden');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function submitAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!access.current || visualPreview) return;
    const data = new FormData(event.currentTarget);
    setBusy(true); setMessage(null); setError(false);
    try {
      const created = await request<Account>('/financial/accounts', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + access.current },
        body: JSON.stringify({ name: data.get('account-name'), account_type: data.get('account-type'), initial_balance: data.get('account-balance') }),
      });
      setAccounts(current => [...current, created]); event.currentTarget.reset(); setMessage('accountCreated');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function submitCreditCard(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!access.current || visualPreview) return;
    const data = new FormData(event.currentTarget);
    setBusy(true); setMessage(null); setError(false);
    try {
      const created = await request<CreditCard>('/financial/credit-cards', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + access.current },
        body: JSON.stringify({ name: data.get('card-name'), credit_limit: data.get('card-limit'), closing_day: Number(data.get('closing-day')), due_day: Number(data.get('due-day')) }),
      });
      setCreditCards(current => [...current, created]); event.currentTarget.reset(); setMessage('cardCreated');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function confirmEmail(token = confirmationToken) {
    if (!token || visualPreview) return;
    setBusy(true); setMessage(null); setError(false);
    try {
      await request<{ email_verified: boolean }>('/email-confirmation/confirm', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ token }),
      });
      setUser(current => current ? { ...current, email_verified: true } : current);
      setConfirmationToken('');
      history.replaceState(null, '', window.location.pathname);
      setMessage('emailConfirmed');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function resendConfirmation() {
    setBusy(true); setMessage(null); setError(false);
    try {
      await request<void>('/email-confirmation', { method: 'POST', headers: access.current ? { Authorization: `Bearer ${access.current}` } : {} });
      setMessage('confirmationSent');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function reviewDeletion() {
    if (!access.current || visualPreview || interactivePreview) return;
    setBusy(true);
    try {
      await request('/account/deletion-preview', { headers: { Authorization: `Bearer ${access.current}` } });
      setDeletionReview(true);
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }
  async function submitDeletion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!access.current || !deletionReview) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    setBusy(true); setMessage(null); setError(false);
    try {
      await request('/account', { method: 'DELETE', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${access.current}` }, body: JSON.stringify({ current_password: data.get('delete-password'), confirmation: data.get('delete-confirmation') }) });
      clearTimeout(timer.current); access.current = null; setUser(null); setManagedSessions([]);
      setCategories([]); setAccounts([]); setCreditCards([]); setPendingEmail(null); setTab('overview');
      setDeletionReview(false); setMode('login'); setMessage('deletionDone');
    } catch (cause) { notify(cause); }
    finally { form.reset(); setBusy(false); }
  }

  async function downloadStatement(format: 'csv' | 'pdf', form: HTMLFormElement) {
    if (!access.current || visualPreview || interactivePreview) return;
    const values = new FormData(form);
    const start = String(values.get('statement-start'));
    const end = String(values.get('statement-end'));
    setBusy(true); setMessage(null); setError(false);
    try {
      const response = await fetch(`${prefix}/financial/exports/${format}?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`, { headers: { Authorization: `Bearer ${access.current}` }, credentials: 'same-origin' });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new ApiError(typeof body.detail === 'string' ? body.detail : 'service_unavailable');
      }
      const url = URL.createObjectURL(await response.blob());
      const anchor = document.createElement('a'); anchor.href = url; anchor.download = `extrato.${format}`; anchor.click(); URL.revokeObjectURL(url);
      setMessage('exportReady');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function logout() {
    setBusy(true); setMessage(null);
    clearTimeout(timer.current);
    try {
      await request<void>('/logout', { method: 'POST', headers: access.current ? { Authorization: `Bearer ${access.current}` } : {} });
      access.current = null; setUser(null); setMessage('sessionEnded'); setError(false);
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function revokeSession(session: ManagedSession) {
    if (!access.current) return;
    setBusy(true); setMessage(null); setError(false);
    try {
      await request<void>(`/sessions/${session.id}/revoke`, {
        method: 'POST', headers: { Authorization: `Bearer ${access.current}` },
      });
      if (session.current) {
        clearTimeout(timer.current); access.current = null; setUser(null); setManagedSessions([]);
        setMessage('sessionEnded');
      } else {
        setManagedSessions(current => current.filter(item => item.id !== session.id));
        setMessage('sessionRevoked');
      }
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function revokeAllSessions() {
    if (!access.current) return;
    setBusy(true); setMessage(null); setError(false);
    try {
      await request<{ revoked_sessions: number }>('/sessions/revoke-all', {
        method: 'POST', headers: { Authorization: `Bearer ${access.current}` },
      });
      clearTimeout(timer.current); access.current = null; setUser(null); setManagedSessions([]);
      setMessage('allSessionsEnded');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function submitQuiz(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const answers = quizQuestions.map(question => Number(form.get(`quiz-${question.id}`)));
    if (answers.length !== 5 || answers.some(answer => !Number.isInteger(answer) || answer < 0 || answer > 2)) {
      notify(new ApiError('invalid_input')); return;
    }
    setBusy(true); setMessage(null); setError(false);
    try {
      const result = await request<{ profile: InvestorProfile }>('/investor-profile', {
        method: 'PUT', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${access.current}` },
        body: JSON.stringify({ answers }),
      });
      setUser(current => current ? { ...current, investor_profile: result.profile } : current);
      setMessage('quizSaved');
    } catch (cause) { notify(cause); } finally { setBusy(false); }
  }

  async function searchCompanies(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = String(new FormData(event.currentTarget).get('company-query') || '').trim();
    if (!query || !access.current) return;
    setBusy(true); setMessage(null); setError(false);
    try {
      const results = await request<PublicCompany[]>(`/api/v1/companies?query=${encodeURIComponent(query)}`, { headers: { Authorization: `Bearer ${access.current}` } });
      setCompanies(results); setSelectedCompany(null); setOfficialDocuments([]); setFinancialIndicators([]);
      if (!results.length) setMessage('companyNotFound');
    } catch (cause) { notify(cause); } finally { setBusy(false); }
  }

  async function selectCompany(company: PublicCompany) {
    if (!access.current) return;
    setBusy(true); setMessage(null); setError(false);
    try {
      const [documents, indicators] = await Promise.all([
        request<OfficialDocument[]>(`/api/v1/companies/${company.id}/documents`, { headers: { Authorization: `Bearer ${access.current}` } }),
        request<FinancialIndicator[]>(`/api/v1/companies/${company.id}/financial-indicators`, { headers: { Authorization: `Bearer ${access.current}` } }),
      ]);
      setSelectedCompany(company); setOfficialDocuments(documents); setFinancialIndicators(indicators);
    } catch (cause) { notify(cause); } finally { setBusy(false); }
  }

  async function watchCompany(company: PublicCompany) {
    if (!access.current) return;
    setBusy(true); setMessage(null); setError(false);
    try {
      await request(`/api/v1/companies/${company.id}/watchlist`, { method: 'POST', headers: { Authorization: `Bearer ${access.current}` } });
      setWatchVersion(version => version + 1);
    } catch (cause) { notify(cause); } finally { setBusy(false); }
  }

  async function checkDocumentLink(document: OfficialDocument) {
    if (!access.current) return;
    setBusy(true); setMessage(null); setError(false);
    try {
      const checked = await request<OfficialDocument>(`/api/v1/companies/documents/${document.id}/link-check`, { method: 'POST', headers: { Authorization: `Bearer ${access.current}` } });
      setOfficialDocuments(current => current.map(item => item.id === checked.id ? checked : item));
      setMessage(checked.link_status === 'available' ? 'linkAvailable' : 'linkBroken');
    } catch (cause) { notify(cause); } finally { setBusy(false); }
  }

  async function searchMarketQuote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const ticker = String(new FormData(event.currentTarget).get('market-ticker') || '').trim();
    if (!ticker || !access.current) return;
    setBusy(true); setMessage(null); setError(false); setManualMarketEntry(false);
    try {
      const quote = await request<MarketQuote>(`/api/v1/market/quotes/${encodeURIComponent(ticker)}`, { headers: { Authorization: `Bearer ${access.current}` } });
      setMarketQuote(quote);
    } catch (cause) {
      setMarketQuote(null);
      if (cause instanceof ApiError && cause.manualEntryPermitted) {
        setManualMarketEntry(true);
        setMessage('marketManualEntry');
      } else notify(cause);
    } finally { setBusy(false); }
  }

  async function submitProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!access.current || visualPreview) return;
    const data = new FormData(event.currentTarget);
    const name = String(data.get('profile-name') || '').trim();
    const email = String(data.get('profile-email') || '').trim();
    const currentPassword = String(data.get('current-password') || '');
    setBusy(true); setMessage(null); setError(false);
    try {
      const body: Record<string, string> = {};
      if (name && name !== user?.name) body.name = name;
      if (email && email !== user?.email) { body.email = email; body.current_password = currentPassword; }
      const profile = await request<Profile>('/profile', { method: 'PATCH', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + access.current }, body: JSON.stringify(body) });
      setUser(profile.user); setPendingEmail(profile.pending_email); setMessage(profile.pending_email ? 'emailChangePending' : 'profileSaved');
      event.currentTarget.reset();
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  async function submitPreferences(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!access.current || visualPreview) return;
    const data = new FormData(event.currentTarget);
    const next: Preferences = {
      language: String(data.get('preference-language')) as Language,
      theme: String(data.get('preference-theme')) as Preferences['theme'],
      in_app_notifications: data.get('in-app') === 'on',
      email_notifications: data.get('email-notifications') === 'on',
      push_notifications: data.get('push-notifications') === 'on',
    };
    setBusy(true); setMessage(null); setError(false);
    try {
      const saved = await request<Preferences>('/profile/preferences', { method: 'PATCH', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + access.current }, body: JSON.stringify(next) });
      setPreferences(saved); setLang(saved.language); setMessage('preferencesSaved');
    } catch (cause) { notify(cause); }
    finally { setBusy(false); }
  }

  function formatSessionInstant(value: string) {
    return new Intl.DateTimeFormat(lang === 'pt' ? 'pt-BR' : 'en-US', {
      dateStyle: 'short', timeStyle: 'short',
    }).format(new Date(value));
  }

  const seconds = Math.max(0, Math.ceil((retryAt - now) / 1000));
  const countdown = `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
  const feedback = <>
    <p className={`message ${error ? 'error' : ''}`} role={error ? 'alert' : 'status'} aria-live="polite">{message ? t[message] : ''}</p>
    {seconds > 0 && <p className="retry-countdown">{t.retryIn} <span aria-live="off">{countdown}</span></p>}
  </>;
  const languageSelect = <div className="language"><label htmlFor="language">{t.language}</label>
    <select id="language" value={lang} onChange={e => setLang(e.target.value as Language)}>
      <option value="pt">Português</option><option value="en">English</option>
    </select>
  </div>;

  if (user && !loading) {
    const live = !visualPreview && !interactivePreview;
    const token = access.current;
    const financial = live && user.email_verified && !!token;
    const pt = lang === 'pt';
    const tabs: [Tab, string][] = [
      ['overview', pt ? 'Visão geral' : 'Overview'], ['transactions', pt ? 'Lançamentos' : 'Transactions'],
      ['sharing', pt ? 'Compartilhado' : 'Shared'],
      ['planning', pt ? 'Planejamento' : 'Planning'], ['investments', pt ? 'Investimentos' : 'Investments'],
      ['taxes', pt ? 'Impostos' : 'Taxes'],
      ['patrimony', pt ? 'Patrimônio' : 'Net worth'], ['financing', pt ? 'Financiamentos' : 'Financing'],
      ['companies', pt ? 'Empresas' : 'Companies'], ['learn', pt ? 'Aprender' : 'Learn'],
      ['account', pt ? 'Minha conta' : 'My account'],
      ...(user.role === 'administrador' ? [['admin', pt ? 'Administração' : 'Admin'] as [Tab, string]] : []),
    ];
    const needsVerification = <p className="hint">{t.financeVerificationHint}</p>;
    const verification = !user.email_verified && <section className="profile notice" aria-labelledby="verify-title">
      <h3 id="verify-title">{t.emailPending}</h3>
      <button onClick={resendConfirmation} disabled={busy}>{busy ? t.waiting : t.resendConfirmation}</button>
      <form onSubmit={event => { event.preventDefault(); void confirmEmail(); }} aria-busy={busy}>
        <div className="field"><label htmlFor="confirmation-token">{t.confirmationToken}</label>
          <input id="confirmation-token" value={confirmationToken} onChange={event => setConfirmationToken(event.target.value)} autoComplete="one-time-code" required disabled={busy}/></div>
        <button type="submit" disabled={busy || !confirmationToken}>{busy ? t.waiting : t.confirmEmail}</button>
      </form>
    </section>;
    const content: Record<Tab, ReactNode> = {
      overview: <>{verification}{financial && token ? <><OnboardingTour token={token} lang={lang} version={tourVersion} onNavigate={next => setTab(next as Tab)} /><Overview token={token} lang={lang} /><div className="grid-2"><HealthScore token={token} lang={lang} /><div className="stack"><ScoreBenchmark token={token} lang={lang} /><Notifications token={token} lang={lang} /></div></div></> : !user.email_verified ? null : <p className="hint">{t.previewMode}</p>}</>,
      transactions: financial && token ? <>
        <Transactions token={token} lang={lang} />
        <div className="grid-2">
          <section className="profile" aria-labelledby="financial-sources-title">
            <h3 id="financial-sources-title">{t.financialSourcesTitle}</h3>
            <ul className="source-list">
              {accounts.map(account => <li key={account.id}><strong>{account.name}</strong><span>{t[account.account_type as 'checking' | 'savings' | 'cash' | 'investment']} · {money(account.initial_balance, lang)}</span></li>)}
              {creditCards.map(card => <li key={card.id}><strong>{card.name}</strong><span>{t.creditLimit}: {money(card.credit_limit, lang)} · {t.closes}: {card.closing_day} · {t.due}: {card.due_day}</span></li>)}
            </ul>
            <form onSubmit={submitAccount} aria-busy={busy}>
              <div className="field"><label htmlFor="account-name">{t.accountName}</label><input id="account-name" name="account-name" maxLength={60} required disabled={busy}/></div>
              <div className="field"><label htmlFor="account-type">{t.accountType}</label><select id="account-type" name="account-type" defaultValue="checking" disabled={busy}><option value="checking">{t.checking}</option><option value="savings">{t.savings}</option><option value="cash">{t.cash}</option><option value="investment">{t.investment}</option></select></div>
              <div className="field"><label htmlFor="account-balance">{t.initialBalance}</label><input id="account-balance" name="account-balance" type="number" step="0.01" defaultValue="0" required disabled={busy}/></div>
              <button type="submit" disabled={busy}>{busy ? t.waiting : t.createAccount}</button>
            </form>
            <form onSubmit={submitCreditCard} aria-busy={busy}>
              <div className="field"><label htmlFor="card-name">{t.cardName}</label><input id="card-name" name="card-name" maxLength={60} required disabled={busy}/></div>
              <div className="field"><label htmlFor="card-limit">{t.creditLimit}</label><input id="card-limit" name="card-limit" type="number" min="0.01" step="0.01" required disabled={busy}/></div>
              <div className="inline-fields">
                <div className="field"><label htmlFor="closing-day">{t.closes}</label><input id="closing-day" name="closing-day" type="number" min="1" max="31" required disabled={busy}/></div>
                <div className="field"><label htmlFor="due-day">{t.due}</label><input id="due-day" name="due-day" type="number" min="1" max="31" required disabled={busy}/></div>
              </div>
              <button type="submit" disabled={busy}>{busy ? t.waiting : t.createCard}</button>
            </form>
          </section>
          <div className="stack">
            <CardInvoice token={token} lang={lang} />
            <section className="profile categories" aria-labelledby="categories-title">
              <h3 id="categories-title">{t.categoriesTitle}</h3>
              <p>{t.categoriesHint}</p>
              <ul>
                {categories.map(category => <li key={category.key} className={category.active ? '' : 'inactive'}>
                  <span className="category-color" style={{ backgroundColor: category.color }} aria-hidden="true"/>
                  <span>{category.name}</span>
                  {category.kind === 'standard' && <button type="button" className="secondary" onClick={() => toggleDefaultCategory(category)} disabled={busy}>{category.active ? t.hideCategory : t.showCategory}</button>}
                </li>)}
              </ul>
              <form onSubmit={submitCategory} aria-busy={busy}>
                <div className="field"><label htmlFor="category-name">{t.categoryName}</label><input id="category-name" name="category-name" maxLength={60} required disabled={busy}/></div>
                <div className="field"><label htmlFor="category-color">{t.categoryColor}</label><input id="category-color" name="category-color" type="color" defaultValue="#173F35" disabled={busy}/></div>
                <button type="submit" disabled={busy}>{busy ? t.waiting : t.createCategory}</button>
              </form>
            </section>
            <section className="profile" aria-labelledby="statement-title">
              <h3 id="statement-title">{t.statementTitle}</h3><p>{t.statementHint}</p>
              <form onSubmit={event => { event.preventDefault(); void downloadStatement('csv', event.currentTarget); }} aria-busy={busy}>
                <div className="inline-fields">
                  <div className="field"><label htmlFor="statement-start">{t.periodStart}</label><input id="statement-start" name="statement-start" type="date" required disabled={busy}/></div>
                  <div className="field"><label htmlFor="statement-end">{t.periodEnd}</label><input id="statement-end" name="statement-end" type="date" required disabled={busy}/></div>
                </div>
                <div className="actions">
                  <button type="submit" disabled={busy}>{t.exportCsv}</button>
                  <button type="button" className="secondary" onClick={event => { const form = event.currentTarget.form; if (form) void downloadStatement('pdf', form); }} disabled={busy}>{t.exportPdf}</button>
                </div>
              </form>
            </section>
          </div>
        </div>
      </> : needsVerification,
      sharing: financial && token ? <Sharing token={token} lang={lang} /> : needsVerification,
      planning: financial && token ? <><Planning token={token} lang={lang} /><Achievements token={token} lang={lang} /><RetirementPlanner token={token} lang={lang} /><NamedAssetGoals token={token} lang={lang} /><FinancialStress token={token} lang={lang} /></> : needsVerification,
      taxes: financial && token ? <Taxes token={token} lang={lang} /> : needsVerification,
      investments: financial && token ? <><Investments token={token} lang={lang} /><PensionComparison token={token} lang={lang} /><div className="grid-2"><InvestmentAllocation token={token} lang={lang} />
        <section className="profile" aria-labelledby="market-title">
          <h3 id="market-title">{t.marketTitle}</h3>
          <p>{t.marketHint}</p>
          <form onSubmit={searchMarketQuote} aria-busy={busy}>
            <div className="field"><label htmlFor="market-ticker">{t.marketTicker}</label><input id="market-ticker" name="market-ticker" minLength={5} maxLength={7} required disabled={busy}/></div>
            <button type="submit" disabled={busy}>{busy ? t.waiting : t.marketSearch}</button>
          </form>
          {marketQuote && <div className="market-reference">
            <p className="indicator-note">{t.marketLocalReference}</p>
            <p><strong>{marketQuote.ticker}</strong> · {marketQuote.asset_kind === 'stock' ? t.marketStock : t.marketFii}</p>
            <p className="market-price">{money(marketQuote.price, lang)} <small>{Number(marketQuote.daily_change_percent) >= 0 ? '+' : ''}{marketQuote.daily_change_percent}%</small></p>
            <p><small>{t.referenceDate} {formatSessionInstant(marketQuote.referenced_at)} · {t.marketValidUntil} {formatSessionInstant(marketQuote.fresh_until)}</small></p>
            <ul className="market-history" aria-label={t.marketHistory}>{marketQuote.history.map(point => <li key={point.quoted_on}>{point.quoted_on}: {money(point.close_price, lang)}</li>)}</ul>
          </div>}
          {manualMarketEntry && <p className="verification">{t.marketManualEntry}</p>}
        </section></div></> : needsVerification,
      patrimony: financial && token ? <><NetWorthItems token={token} lang={lang} /><NetWorthHistory token={token} lang={lang} /><NetWorthHeatmap token={token} lang={lang} /></> : needsVerification,
      financing: financial && token ? <><Financing token={token} lang={lang} /><FinancingComparison token={token} lang={lang} /><ConfirmFinancing token={token} lang={lang} /></> : needsVerification,
      companies: live && token ? <>
        <section className="profile" aria-labelledby="companies-title">
          <h3 id="companies-title">{t.companiesTitle}</h3>
          <p>{t.companiesHint}</p>
          <form onSubmit={searchCompanies} aria-busy={busy}>
            <div className="field"><label htmlFor="company-query">{t.companySearch}</label><input id="company-query" name="company-query" minLength={1} maxLength={120} required disabled={busy}/></div>
            <button type="submit" disabled={busy}>{busy ? t.waiting : t.searchCompanies}</button>
          </form>
          {companies.length > 0 && <ul className="company-results">
            {companies.map(company => <li key={company.id}><button type="button" className="secondary" onClick={() => void selectCompany(company)} disabled={busy}>{company.ticker} — {company.legal_name}</button><small>{company.cnpj} · {company.sector}</small>
              <button type="button" className="secondary" onClick={() => void watchCompany(company)} disabled={busy}>{pt ? 'Acompanhar' : 'Watch'}</button></li>)}
          </ul>}
          {selectedCompany && <div className="company-documents">
            <h4>{selectedCompany.ticker} — {selectedCompany.legal_name}</h4>
            <p className="privacy-note">{t.cvmDisclaimer}</p>
            <h5>{t.financialIndicatorsTitle}</h5>
            {financialIndicators.length === 0 ? <p>{t.noFinancialIndicators}</p> : <>
              <p className="indicator-note">{t.indicatorsLocalFixture}</p>
              <div className="indicator-table-wrap" tabIndex={0}><table>
                <caption>{t.financialIndicatorsCaption}</caption>
                <thead><tr><th>{t.indicatorMetric}</th><th>{t.indicatorPeriod}</th><th>{t.indicatorValue}</th><th>{t.indicatorStatus}</th><th>{t.indicatorSource}</th></tr></thead>
                <tbody>{financialIndicators.map(indicator => <tr key={indicator.id} className={indicator.effective ? '' : 'superseded'}>
                  <td>{indicator.metric === 'net_revenue' ? t.netRevenue : indicator.metric === 'net_income' ? t.netIncome : t.equity}</td><td>{indicator.reference_period}<br/><small>{t.referenceDate} {indicator.reference_date}</small></td><td>{new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', { maximumFractionDigits: 2 }).format(Number(indicator.value))} {t.thousandsOfReais}</td><td>{indicator.effective ? t.currentIndicator : t.restatedIndicator}</td><td><a href={indicator.source_url} target="_blank" rel="noopener noreferrer">{indicator.source_name}</a><br/><small>{t.syncedAt} {indicator.synced_at.slice(0, 10)}</small></td>
                </tr>)}</tbody>
              </table></div>
              <div className="indicator-chart" role="img" aria-label={t.indicatorChartAlternative}>
                <h6>{t.indicatorEvolution}</h6>
                {(['net_revenue', 'net_income', 'equity'] as const).map(metric => {
                  const rows = financialIndicators.filter(item => item.metric === metric && item.effective);
                  const maximum = Math.max(...rows.map(item => Math.abs(Number(item.value))), 1);
                  return <div className="indicator-series" key={metric}><strong>{metric === 'net_revenue' ? t.netRevenue : metric === 'net_income' ? t.netIncome : t.equity}</strong>{rows.map(item => <div className="indicator-bar" key={item.id}><span>{item.reference_period}</span><i style={{ width: `${Math.max(3, Math.abs(Number(item.value)) / maximum * 100)}%` }} /><b>{new Intl.NumberFormat(lang === 'pt' ? 'pt-BR' : 'en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(Number(item.value))}</b></div>)}</div>;
                })}
              </div>
            </>}
            {officialDocuments.length === 0 ? <p>{t.noDocuments}</p> : <ul>
              {officialDocuments.map(document => <li key={document.id}>
                <strong>{document.document_type}</strong> — {document.subject} ({document.reference_period})<br/>
                <small>{t.deliveredAt} {document.delivered_at} · {t.documentStatus}: {document.status} · {t.linkStatus}: {document.link_status}</small><br/>
                <a href={document.official_url} target="_blank" rel="noopener noreferrer">{t.openOfficialDocument}</a>{' '}
                <button type="button" className="secondary" onClick={() => void checkDocumentLink(document)} disabled={busy}>{t.checkLink}</button>
              </li>)}
            </ul>}
          </div>}
        </section>
        <Watchlist token={token} lang={lang} version={watchVersion} />
      </> : needsVerification,
      learn: live && token ? <><ReopenTour token={token} lang={lang} onReopen={() => { setTourVersion(version => version + 1); setTab('overview'); }} /><EducationCenter token={token} lang={lang} /></> : null,
      account: <>
        {verification}
        <div className="grid-2">
          <div className="stack">
            <section className="profile" aria-labelledby="profile-title">
              <h3 id="profile-title">{t.profileTitle}</h3>
              <p className="email">{user.email}</p>
              {pendingEmail && <p className="verification" role="status">{t.emailChangePending} {pendingEmail}</p>}
              <p className="verification">{user.email_verified ? t.emailVerified : t.emailPending}</p>
              <form onSubmit={submitProfile} aria-busy={busy}>
                <div className="field"><label htmlFor="profile-name">{t.name}</label><input id="profile-name" name="profile-name" defaultValue={user.name} maxLength={100} disabled={busy}/></div>
                <div className="field"><label htmlFor="profile-email">{t.email}</label><input id="profile-email" name="profile-email" type="email" defaultValue={user.email} maxLength={254} disabled={busy}/></div>
                <div className="field"><label htmlFor="current-password">{t.currentPassword}</label><input id="current-password" name="current-password" type="password" autoComplete="current-password" minLength={8} maxLength={128} disabled={busy}/><small>{t.emailChangeHint}</small></div>
                <button type="submit" disabled={busy}>{busy ? t.waiting : t.saveProfile}</button>
              </form>
            </section>
            <section className="profile" aria-labelledby="preferences-title">
              <h3 id="preferences-title">{t.preferencesTitle}</h3>
              <form onSubmit={submitPreferences} aria-busy={busy}>
                <div className="field"><label htmlFor="preference-language">{t.language}</label><select id="preference-language" name="preference-language" defaultValue={preferences.language} disabled={busy}><option value="pt">Português</option><option value="en">English</option></select></div>
                <div className="field"><label htmlFor="preference-theme">{t.theme}</label><select id="preference-theme" name="preference-theme" defaultValue={preferences.theme} disabled={busy}><option value="light">{t.lightTheme}</option><option value="dark">{t.darkTheme}</option></select></div>
                <label className="check"><input type="checkbox" name="in-app" defaultChecked={preferences.in_app_notifications} disabled={busy}/>{t.inAppNotifications}</label>
                <label className="check"><input type="checkbox" name="email-notifications" defaultChecked={preferences.email_notifications} disabled={busy}/>{t.emailNotifications}</label>
                <label className="check"><input type="checkbox" name="push-notifications" defaultChecked={preferences.push_notifications} disabled={busy}/>{t.pushNotifications}</label>
                <button type="submit" disabled={busy}>{busy ? t.waiting : t.savePreferences}</button>
              </form>
            </section>
            <section className="profile" aria-labelledby="password-title">
              <h3 id="password-title">{t.passwordTitle}</h3>
              <form onSubmit={submitPasswordChange} aria-busy={busy}>
                <div className="field"><label htmlFor="change-current-password">{t.currentPassword}</label><input id="change-current-password" name="change-current-password" type="password" autoComplete="current-password" minLength={8} maxLength={128} required disabled={busy}/></div>
                <div className="field"><label htmlFor="change-new-password">{t.newPassword}</label><input id="change-new-password" name="change-new-password" type="password" autoComplete="new-password" minLength={8} maxLength={128} required disabled={busy}/></div>
                <button type="submit" disabled={busy}>{busy ? t.waiting : t.changePassword}</button>
              </form>
            </section>
          </div>
          <div className="stack">
            <section className="profile" aria-labelledby="investor-profile-title">
              <h3 id="investor-profile-title">{t.investorProfileTitle}</h3>
              <p>{user.investor_profile ? `${t.investorProfileCurrent}: ${user.investor_profile === 'conservador' ? t.profileConservador : user.investor_profile === 'moderado' ? t.profileModerado : t.profileArrojado}` : t.investorProfileHint}</p>
              {quizQuestions.length > 0 && <form onSubmit={submitQuiz} aria-busy={busy}>
                {quizQuestions.map(question => <fieldset key={question.id} className="field">
                  <legend>{question.prompt}</legend>
                  {question.options.map((option, index) => <label className="check" key={option}>
                    <input type="radio" name={`quiz-${question.id}`} value={index} required disabled={busy}/>{option}
                  </label>)}
                </fieldset>)}
                <button type="submit" disabled={busy}>{busy ? t.waiting : t.saveQuiz}</button>
              </form>}
            </section>
            <section className="sessions profile" aria-labelledby="sessions-title">
              <div className="sessions-heading">
                <h3 id="sessions-title">{t.sessionsTitle}</h3>
                <button type="button" className="secondary" onClick={revokeAllSessions} disabled={busy || !managedSessions.length}>
                  {busy ? t.waiting : t.endAllSessions}
                </button>
              </div>
              <p className="hint">{t.sessionHint}</p>
              <ul>
                {managedSessions.map(session => <li key={session.id}>
                  <div>
                    <strong>{session.current ? t.sessionCurrent : t.sessionOther}</strong>
                    <span>{t.sessionStarted} {formatSessionInstant(session.started_at)}</span>
                    <span>{t.sessionExpires} {formatSessionInstant(session.expires_at)}</span>
                  </div>
                  <button type="button" className="secondary" onClick={() => revokeSession(session)} disabled={busy}>
                    {session.current ? t.endCurrentSession : t.endSession}
                  </button>
                </li>)}
              </ul>
            </section>
            {financial && token && <ExternalIntegrations token={token} lang={lang} />}
            {live && <section className="profile danger-zone" aria-labelledby="delete-title">
              <h3 id="delete-title">{t.deleteAccount}</h3>
              {!deletionReview ? <button type="button" onClick={reviewDeletion} disabled={busy}>{t.deletionReview}</button> : <>
                <p>{t.deletionScope}</p>
                <form onSubmit={submitDeletion} aria-busy={busy}>
                  <div className="field"><label htmlFor="delete-password">{t.currentPassword}</label><input id="delete-password" name="delete-password" type="password" autoComplete="current-password" maxLength={128} required disabled={busy}/></div>
                  <div className="field"><label htmlFor="delete-confirmation">{t.deletionText}</label><input id="delete-confirmation" name="delete-confirmation" pattern="EXCLUIR MINHA CONTA" autoComplete="off" required disabled={busy}/></div>
                  <button type="submit" disabled={busy}>{t.deleteAccount}</button>
                  <button type="button" className="secondary" onClick={() => setDeletionReview(false)} disabled={busy}>{t.deletionCancel}</button>
                </form>
              </>}
            </section>}
          </div>
        </div>
      </>,
      admin: <>
        {adminUsers && <section className="profile" aria-labelledby="admin-users-title">
          <h3 id="admin-users-title">{t.adminUsersTitle}</h3>
          <p>{t.adminUsersHint.replace('{total}', String(adminUsers.total))}</p>
          <ul className="source-list">
            {adminUsers.items.map(member => <li key={member.id}><strong>{member.name}</strong><span>{member.email} · {member.status} · {formatSessionInstant(member.created_at)}</span></li>)}
          </ul>
        </section>}
        {live && token && <div className="grid-2"><AdminProfileDistribution token={token} lang={lang} /><AdminEngagement token={token} lang={lang} /></div>}
      </>,
    };
    const visibleTabs = live ? tabs : tabs.filter(([key]) => key === 'account');
    const current = visibleTabs.some(([key]) => key === tab) ? tab : visibleTabs[0][0];
    return <div className="app">
      <header className="topbar">
        <p className="brand">FinNova<span aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 19 19 5M5 5h14v14"/></svg></span></p>
        <div className="topbar-user">
          <h2 ref={heading} tabIndex={-1}>{t.greeting} {user.name}</h2>
          <p className="eyebrow">{t.authenticated} · {user.email_verified ? t.emailVerified : t.emailPending}</p>
        </div>
        <div className="topbar-actions">
          {languageSelect}
          <button onClick={logout} disabled={busy} className="secondary">{busy ? t.waiting : t.logout}</button>
        </div>
      </header>
      <nav className="tabs" aria-label={pt ? 'Seções do FinNova' : 'FinNova sections'}>
        {visibleTabs.map(([key, label]) => <button key={key} type="button" aria-current={current === key ? 'page' : undefined} onClick={() => { setTab(key); setMessage(null); }}>{label}</button>)}
      </nav>
      <main className="content">
        {interactivePreview && <aside className="demo-notice" aria-label={t.demoTitle}><p><strong>{t.demoTitle}</strong><br/>{t.demoHint}</p></aside>}
        <p className="privacy-note">{t.privacyUsage}</p>
        {content[current]}
        {feedback}
      </main>
    </div>;
  }

  return <main className="layout">
    <section className="intro" aria-label="FinNova">
      <p className="brand">FinNova<span aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 19 19 5M5 5h14v14"/></svg></span></p>
      <h1>{t.welcome}</h1><p>{t.intro}</p>
      <div className="illustration" aria-hidden="true"><span/><span/><span/><span/><span/></div>
    </section>
    <section className="panel">
      {languageSelect}
      <div className="card">
        {interactivePreview && <aside className="demo-notice" aria-label={t.demoTitle}>
          <p><strong>{t.demoTitle}</strong><br/>{t.demoHint}</p>
          <p className="demo-credentials">art@exemplo.com · SenhaForte123</p>
          <div className="demo-actions">
            <button type="button" onClick={() => {
              advanceDemo(); setNow(nowMs()); setMessage(null); setRetryAt(0);
            }}>{t.advanceDemo}</button>
            <button type="button" onClick={() => {
              resetDemo(); clearTimeout(timer.current); access.current = null;
              setUser(null); setMode('login'); setRetryAt(0); setMessage(null); setError(false);
            }}>{t.resetDemo}</button>
          </div>
        </aside>}
        {visualPreview && <p className="preview-notice" role="note">{t.previewMode}</p>}
        {loading ? <p role="status">{t.loading}</p> : passwordResetToken ? <>
          <h2 ref={heading} tabIndex={-1}>{t.resetPasswordTitle}</h2>
          <p>{t.resetPasswordHint}</p>
          <form onSubmit={submitPasswordReset} aria-busy={busy}>
            <div className="field"><label htmlFor="new-password">{t.newPassword}</label><input id="new-password" name="new-password" type="password" autoComplete="new-password" minLength={8} maxLength={128} required disabled={busy}/></div>
            <button type="submit" disabled={busy}>{busy ? t.waiting : t.resetPassword}</button>
          </form>
        </> : <>
          <nav className="switcher" aria-label={t.loginTitle}>
            <button aria-pressed={mode === 'login'} onClick={() => { setMode('login'); setMessage(null); }} disabled={busy}>{t.login}</button>
            <button aria-pressed={mode === 'register'} onClick={() => { setMode('register'); setMessage(null); }} disabled={busy}>{t.register}</button>
            <button aria-pressed={mode === 'recovery'} onClick={() => { setMode('recovery'); setMessage(null); }} disabled={busy}>{t.forgotPassword}</button>
          </nav>
          <h2 ref={heading} tabIndex={-1}>{mode === 'login' ? t.loginTitle : mode === 'register' ? t.registerTitle : t.passwordRecoveryTitle}</h2>
          <form onSubmit={submit} aria-busy={busy}>
            {mode === 'register' && <div className="field"><label htmlFor="name">{t.name}</label>
              <input id="name" name="name" autoComplete="name" maxLength={100} required disabled={busy}/></div>}
            <div className="field"><label htmlFor="email">{t.email}</label>
              <input id="email" name="email" type="email" autoComplete="username" maxLength={254} required disabled={busy}
                onChange={() => { if (retryAt) { setRetryAt(0); setMessage(null); } }}/></div>
            {mode !== 'recovery' && <div className="field"><label htmlFor="password">{t.password}</label>
              <input id="password" name="password" type="password" autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
                minLength={8} maxLength={128} aria-describedby="password-help" required disabled={busy}/>
              <small id="password-help">{t.passwordHelp}</small></div>}
            <button type="submit" disabled={busy || visualPreview}>{busy ? t.waiting : mode === 'login' ? t.submitLogin : mode === 'register' ? t.submitRegister : t.requestPasswordRecovery}</button>
          </form>
        </>}
        {feedback}
      </div>
    </section>
  </main>;
}

createRoot(document.getElementById('root')!).render(<App/>);
