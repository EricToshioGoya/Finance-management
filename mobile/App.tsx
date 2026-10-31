import { StatusBar } from 'expo-status-bar';
import * as SecureStore from 'expo-secure-store';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { api, ApiError, newIdempotencyKey } from './src/api';
import { currentCompetence, money, today } from './src/format';

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
    setError(''); setStatus('');
    try {
      await api('/auth/financial/expenses', token, {
        method: 'POST', headers: { 'Idempotency-Key': newIdempotencyKey() }, // C-16: reenvio não duplica
        body: JSON.stringify({
          description, amount: amount.replace(',', '.'), category_key: category, occurred_on: today(),
          account_id: source.startsWith('a:') ? source.slice(2) : null, credit_card_id: source.startsWith('c:') ? source.slice(2) : null,
        }),
      });
      setDescription(''); setAmount(''); setStatus('Despesa registrada.');
    } catch (cause) { setError(describe(cause)); }
  }
  return <View>
    <Text style={styles.sectionTitle}>Nova despesa (hoje)</Text>
    <Text style={styles.label}>Descrição</Text>
    <TextInput style={styles.input} value={description} onChangeText={setDescription} maxLength={100} accessibilityLabel="Descrição" />
    <Text style={styles.label}>Valor (R$)</Text>
    <TextInput style={styles.input} value={amount} onChangeText={setAmount} keyboardType="decimal-pad" accessibilityLabel="Valor em reais" />
    <Text style={styles.label}>Categoria</Text>
    <Chips options={categories.map(item => ({ id: item.key, name: item.name }))} selected={category} onSelect={setCategory} />
    <Text style={styles.label}>Pago com</Text>
    <Chips options={sources} selected={source} onSelect={setSource} />
    {!!error && <Text style={styles.error} accessibilityRole="alert">{error}</Text>}
    {!!status && <Text style={styles.positive}>{status}</Text>}
    <Pressable style={styles.button} onPress={() => void submit()} disabled={!description || !amount || !category || !source} accessibilityRole="button"><Text style={styles.buttonText}>Registrar</Text></Pressable>
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

const green = '#173f35';
const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  screen: { flex: 1, backgroundColor: '#f7f8f4' },
  loginScreen: { padding: 24, justifyContent: 'center', backgroundColor: '#f7f8f4' },
  loginBrand: { fontSize: 32, fontWeight: '800', color: green, marginBottom: 24 },
  loginTitle: { fontSize: 24, fontWeight: '700', color: green, marginBottom: 16 },
  header: { backgroundColor: green, paddingHorizontal: 16, paddingTop: 16, paddingBottom: 12, flexDirection: 'row', alignItems: 'center', gap: 12 },
  brand: { color: '#c4e8aa', fontWeight: '800', fontSize: 18 },
  greeting: { color: '#fff', fontWeight: '700', flex: 1 },
  link: { color: '#c4e8aa', fontWeight: '700', paddingVertical: 6 },
  tabs: { flexDirection: 'row', backgroundColor: '#fff', borderBottomWidth: 1, borderColor: '#d3ddd5' },
  tab: { flex: 1, paddingVertical: 14, alignItems: 'center', borderBottomWidth: 3, borderColor: 'transparent' },
  tabActive: { borderColor: green },
  tabText: { color: '#36574a', fontWeight: '600' },
  tabTextActive: { color: green },
  body: { padding: 16, gap: 8 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: green, marginBottom: 8 },
  label: { fontWeight: '600', color: green, marginTop: 12, marginBottom: 6 },
  input: { borderWidth: 1, borderColor: '#758b7f', borderRadius: 8, padding: 12, backgroundColor: '#fff', minHeight: 48 },
  button: { backgroundColor: green, borderRadius: 8, paddingVertical: 14, alignItems: 'center', marginTop: 16, minHeight: 48 },
  buttonText: { color: '#fff', fontWeight: '700' },
  secondary: { backgroundColor: '#fff', borderWidth: 1, borderColor: green },
  secondaryText: { color: green, fontWeight: '700' },
  error: { color: '#a02220', marginTop: 8 },
  hint: { color: '#4f655a', marginTop: 12 },
  kpi: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#d3ddd5', borderRadius: 10, padding: 14, marginBottom: 8 },
  kpiLabel: { color: '#4f655a', fontWeight: '600', textTransform: 'uppercase', fontSize: 12 },
  kpiValue: { fontSize: 22, fontWeight: '700', marginTop: 4 },
  positive: { color: '#1d6b4a' },
  negative: { color: '#a02220' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: { borderWidth: 1, borderColor: '#b0bdb3', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 8, minHeight: 40 },
  chipActive: { backgroundColor: green, borderColor: green },
  chipText: { color: green },
  chipTextActive: { color: '#fff' },
  notice: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#d3ddd5', borderRadius: 8, padding: 12, marginBottom: 8, gap: 4 },
  noticeTitle: { fontWeight: '700', color: green },
  read: { opacity: 0.6 },
});
