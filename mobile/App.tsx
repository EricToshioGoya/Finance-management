import { StatusBar } from 'expo-status-bar';
import * as SecureStore from 'expo-secure-store';
import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { api, ApiError, newIdempotencyKey } from './src/api';
import { currentCompetence, money, parseAmount, today } from './src/format';

// Cliente móvel mínimo (RNF-05): login, resumo do mês, lançamento de despesa e notificações,
// usando a mesma API /api/v1 do cliente web. O token de acesso fica no armazenamento seguro.
type Summary = { total: string; expenses: string; balance_variation: string; recurring_income: string; one_time_income: string; bonus: string };
type Category = { key: string; name: string; active: boolean };
type Source = { id: string; name: string };
type Notice = { id: string; title: string; message: string; read_at: string | null };
type Tab = 'summary' | 'expense' | 'notices';

const TOKEN_KEY = 'finnova-access-token';
const messages: Record<string, string> = {
  invalid_credentials: 'E-mail ou senha incorretos.',
  email_not_verified: 'Confirme seu e-mail pela versão web para usar as funções financeiras.',
  account_locked: 'Acesso temporariamente indisponível. Tente mais tarde.',
};
const describe = (cause: unknown) => (cause instanceof ApiError && messages[cause.message]) || 'Não foi possível concluir. Verifique a conexão e tente novamente.';

export default function App() {
  const [token, setToken] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>('summary');

  const restore = useCallback(async () => {
    const saved = await SecureStore.getItemAsync(TOKEN_KEY);
    if (saved) {
      try { setName((await api<{ name: string }>('/auth/me', saved)).name); setToken(saved); }
      catch { await SecureStore.deleteItemAsync(TOKEN_KEY); }
    }
    setLoading(false);
  }, []);
  useEffect(() => { void restore(); }, [restore]);

  async function signIn(newToken: string) {
    await SecureStore.setItemAsync(TOKEN_KEY, newToken);
    setName((await api<{ name: string }>('/auth/me', newToken)).name);
    setToken(newToken);
  }
  async function signOut() {
    await api('/auth/logout', token, { method: 'POST' }).catch(() => undefined);
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    setToken(null);
  }

  if (loading) return <SafeAreaView style={styles.center}><ActivityIndicator /></SafeAreaView>;
  if (!token) return <Login onSignedIn={signIn} />;
  return <SafeAreaView style={styles.screen}>
    <StatusBar style="light" />
    <View style={styles.header}>
      <Text style={styles.brand}>FinNova</Text>
      <Text style={styles.greeting} accessibilityRole="header">Olá, {name}</Text>
      <Pressable onPress={() => void signOut()} accessibilityRole="button"><Text style={styles.link}>Sair</Text></Pressable>
    </View>
    <View style={styles.tabs} accessibilityRole="tablist">
      {([['summary', 'Resumo'], ['expense', 'Lançar'], ['notices', 'Avisos']] as [Tab, string][]).map(([key, label]) =>
        <Pressable key={key} onPress={() => setTab(key)} accessibilityRole="tab" accessibilityState={{ selected: tab === key }} style={[styles.tab, tab === key && styles.tabActive]}>
          <Text style={[styles.tabText, tab === key && styles.tabTextActive]}>{label}</Text>
        </Pressable>)}
    </View>
    <ScrollView contentContainerStyle={styles.body}>
      {tab === 'summary' && <MonthSummary token={token} />}
      {tab === 'expense' && <ExpenseForm token={token} />}
      {tab === 'notices' && <Notices token={token} />}
    </ScrollView>
  </SafeAreaView>;
}

function Login({ onSignedIn }: { onSignedIn: (token: string) => Promise<void> }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit() {
    setBusy(true); setError('');
    try {
      const session = await api<{ access_token: string }>('/auth/login', null, { method: 'POST', body: JSON.stringify({ email, password }) });
      await onSignedIn(session.access_token);
    } catch (cause) { setError(describe(cause)); setPassword(''); }
    finally { setBusy(false); }
  }
  return <SafeAreaView style={[styles.screen, styles.loginScreen]}>
    <StatusBar style="light" />
    <Text style={styles.loginBrand}>FinNova</Text>
    <Text style={styles.loginTitle} accessibilityRole="header">Acesse sua conta</Text>
    <Text style={styles.label}>E-mail</Text>
    <TextInput style={styles.input} value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" autoComplete="email" accessibilityLabel="E-mail" />
    <Text style={styles.label}>Senha</Text>
    <TextInput style={styles.input} value={password} onChangeText={setPassword} secureTextEntry autoComplete="password" accessibilityLabel="Senha" />
    {!!error && <Text style={styles.error} accessibilityRole="alert">{error}</Text>}
    <Pressable style={styles.button} onPress={() => void submit()} disabled={busy || !email || password.length < 8} accessibilityRole="button">
      <Text style={styles.buttonText}>{busy ? 'Aguarde…' : 'Entrar na conta'}</Text>
    </Pressable>
    <Text style={styles.hint}>Cadastro, confirmação de e-mail e configurações estão na versão web.</Text>
  </SafeAreaView>;
}

function MonthSummary({ token }: { token: string }) {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState('');
  const competence = currentCompetence();
  const load = useCallback(async () => {
    try { setSummary(await api<Summary>(`/auth/financial/balance-summary?competence=${competence}`, token)); setError(''); }
    catch (cause) { setError(describe(cause)); }
  }, [token, competence]);
  useEffect(() => { void load(); }, [load]);
  return <View>
    <Text style={styles.sectionTitle}>Resumo de {competence}</Text>
    {!!error && <Text style={styles.error}>{error}</Text>}
    {summary && <>
      <Kpi label="Receitas" value={money(summary.total)} tone="positive" />
      <Kpi label="Despesas" value={money(summary.expenses)} tone="negative" />
      <Kpi label="Saldo do mês" value={money(summary.balance_variation)} tone={Number(summary.balance_variation) >= 0 ? 'positive' : 'negative'} />
      <Text style={styles.hint}>Recorrentes {money(summary.recurring_income)} · pontuais {money(summary.one_time_income)} · bônus {money(summary.bonus)}</Text>
    </>}
    <Pressable style={[styles.button, styles.secondary]} onPress={() => void load()} accessibilityRole="button"><Text style={styles.secondaryText}>Atualizar</Text></Pressable>
  </View>;
}

function Kpi({ label, value, tone }: { label: string; value: string; tone: 'positive' | 'negative' }) {
  return <View style={styles.kpi}><Text style={styles.kpiLabel}>{label}</Text><Text style={[styles.kpiValue, tone === 'positive' ? styles.positive : styles.negative]}>{value}</Text></View>;
}

function ExpenseForm({ token }: { token: string }) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [description, setDescription] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('');
  const [source, setSource] = useState('');
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  // C-16/RNF-24: a mesma chave vale para toque duplo e reenvio após falha; muda só com novos dados.
  const pendingKey = useRef<string | null>(null);
  const edit = <T,>(setter: (value: T) => void) => (value: T) => { pendingKey.current = null; setter(value); };
  useEffect(() => {
    void Promise.all([
      api<Category[]>('/auth/categories', token),
      api<{ accounts: Source[]; credit_cards: Source[] }>('/auth/financial/sources', token),
    ]).then(([cats, found]) => {
      setCategories(cats.filter(item => item.active));
      setSources([...found.accounts.map(item => ({ id: `a:${item.id}`, name: item.name })), ...found.credit_cards.map(item => ({ id: `c:${item.id}`, name: `Cartão ${item.name}` }))]);
    }).catch(cause => setError(describe(cause)));
  }, [token]);
  async function submit() {
    if (busy) return;
    setError(''); setStatus('');
    const value = parseAmount(amount);
    if (value === null) { setError('Informe um valor válido, por exemplo 1.234,56.'); return; }
    const key = (pendingKey.current ??= newIdempotencyKey());
    setBusy(true);
    try {
      await api('/auth/financial/expenses', token, {
        method: 'POST', headers: { 'Idempotency-Key': key },
        body: JSON.stringify({
          description, amount: value, category_key: category, occurred_on: today(),
          account_id: source.startsWith('a:') ? source.slice(2) : null, credit_card_id: source.startsWith('c:') ? source.slice(2) : null,
        }),
      });
      pendingKey.current = null;
      setDescription(''); setAmount(''); setStatus('Despesa registrada.');
    } catch (cause) { setError(describe(cause)); }
    finally { setBusy(false); }
  }
  return <View>
    <Text style={styles.sectionTitle}>Nova despesa (hoje)</Text>
    <Text style={styles.label}>Descrição</Text>
    <TextInput style={styles.input} value={description} onChangeText={edit(setDescription)} maxLength={100} accessibilityLabel="Descrição" />
    <Text style={styles.label}>Valor (R$)</Text>
    <TextInput style={styles.input} value={amount} onChangeText={edit(setAmount)} keyboardType="decimal-pad" accessibilityLabel="Valor em reais" />
    <Text style={styles.label}>Categoria</Text>
    <Chips options={categories.map(item => ({ id: item.key, name: item.name }))} selected={category} onSelect={edit(setCategory)} />
    <Text style={styles.label}>Pago com</Text>
    <Chips options={sources} selected={source} onSelect={edit(setSource)} />
    {!!error && <Text style={styles.error} accessibilityRole="alert">{error}</Text>}
    {!!status && <Text style={styles.positive}>{status}</Text>}
    <Pressable style={styles.button} onPress={() => void submit()} disabled={busy || !description || !amount || !category || !source} accessibilityRole="button" accessibilityState={{ busy, disabled: busy }}><Text style={styles.buttonText}>{busy ? 'Registrando…' : 'Registrar'}</Text></Pressable>
  </View>;
}

function Chips({ options, selected, onSelect }: { options: { id: string; name: string }[]; selected: string; onSelect: (id: string) => void }) {
  return <View style={styles.chips}>{options.map(option =>
    <Pressable key={option.id} onPress={() => onSelect(option.id)} accessibilityRole="radio" accessibilityState={{ checked: selected === option.id }} style={[styles.chip, selected === option.id && styles.chipActive]}>
      <Text style={selected === option.id ? styles.chipTextActive : styles.chipText}>{option.name}</Text>
    </Pressable>)}</View>;
}

function Notices({ token }: { token: string }) {
  const [items, setItems] = useState<Notice[]>([]);
  const load = useCallback(async () => { setItems(await api<Notice[]>('/notifications', token).catch(() => [])); }, [token]);
  useEffect(() => { void load(); }, [load]);
  return <View>
    <Text style={styles.sectionTitle}>Notificações</Text>
    {items.length === 0 && <Text style={styles.hint}>Nenhuma notificação.</Text>}
    {items.map(item => <View key={item.id} style={[styles.notice, item.read_at ? styles.read : null]}>
      <Text style={styles.noticeTitle}>{item.title}</Text><Text>{item.message}</Text>
      {!item.read_at && <Pressable onPress={() => void api(`/notifications/${item.id}/read`, token, { method: 'PATCH' }).then(load)} accessibilityRole="button"><Text style={styles.link}>Marcar como lida</Text></Pressable>}
    </View>)}
  </View>;
}

// Mesmos tokens do web (frontend/src/style.css): azul-ardósia; verde só para valor positivo.
const color = {
  bg: '#f7f8fa', surface: '#ffffff', surface2: '#f1f4f9', border: '#e3e8ef', borderStrong: '#cbd5e1',
  text: '#1f2937', muted: '#5b6472', primary: '#3b5bdb', header: '#1e293b', accent: '#a5b4fc',
  positive: '#15803d', negative: '#b42318',
};
const shadow = { shadowColor: '#0f172a', shadowOpacity: 0.06, shadowRadius: 10, shadowOffset: { width: 0, height: 3 }, elevation: 1 };
const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  screen: { flex: 1, backgroundColor: color.bg },
  loginScreen: { padding: 24, justifyContent: 'center', backgroundColor: color.bg },
  loginBrand: { fontSize: 32, fontWeight: '800', color: color.header, marginBottom: 24 },
  loginTitle: { fontSize: 24, fontWeight: '700', color: color.text, marginBottom: 16 },
  header: { backgroundColor: color.header, paddingHorizontal: 16, paddingTop: 16, paddingBottom: 12, flexDirection: 'row', alignItems: 'center', gap: 12 },
  brand: { color: color.accent, fontWeight: '800', fontSize: 18 },
  greeting: { color: '#fff', fontWeight: '700', flex: 1 },
  link: { color: color.accent, fontWeight: '700', paddingVertical: 6 },
  tabs: { flexDirection: 'row', backgroundColor: color.surface, borderBottomWidth: 1, borderColor: color.border },
  tab: { flex: 1, paddingVertical: 14, alignItems: 'center', borderBottomWidth: 2, borderColor: 'transparent' },
  tabActive: { borderColor: color.primary },
  tabText: { color: color.muted, fontWeight: '600' },
  tabTextActive: { color: color.primary },
  body: { padding: 16, gap: 8 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: color.text, marginBottom: 8 },
  label: { fontWeight: '600', color: color.text, marginTop: 12, marginBottom: 6 },
  input: { borderWidth: 1, borderColor: color.borderStrong, borderRadius: 10, padding: 12, backgroundColor: color.surface, color: color.text, minHeight: 48 },
  button: { backgroundColor: color.primary, borderRadius: 10, paddingVertical: 14, alignItems: 'center', marginTop: 16, minHeight: 48 },
  buttonText: { color: '#fff', fontWeight: '700' },
  secondary: { backgroundColor: color.surface, borderWidth: 1, borderColor: color.borderStrong },
  secondaryText: { color: color.text, fontWeight: '700' },
  error: { color: color.negative, marginTop: 8 },
  hint: { color: color.muted, marginTop: 12 },
  kpi: { backgroundColor: color.surface, borderWidth: 1, borderColor: color.border, borderRadius: 12, padding: 14, marginBottom: 8, ...shadow },
  kpiLabel: { color: color.muted, fontWeight: '600', textTransform: 'uppercase', fontSize: 12 },
  kpiValue: { fontSize: 22, fontWeight: '700', marginTop: 4 },
  positive: { color: color.positive },
  negative: { color: color.negative },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: { borderWidth: 1, borderColor: color.border, backgroundColor: color.surface, borderRadius: 20, paddingHorizontal: 12, paddingVertical: 8, minHeight: 40 },
  chipActive: { backgroundColor: color.primary, borderColor: color.primary },
  chipText: { color: color.text },
  chipTextActive: { color: '#fff' },
  notice: { backgroundColor: color.surface, borderWidth: 1, borderColor: color.border, borderRadius: 12, padding: 12, marginBottom: 8, gap: 4 },
  noticeTitle: { fontWeight: '700', color: color.text },
  read: { opacity: 0.6 },
});
