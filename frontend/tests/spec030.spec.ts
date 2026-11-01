import { expect, test, type Page } from '@playwright/test';
import { randomUUID } from 'node:crypto';

// SPEC-030 (mapa de calor patrimonial): cláusulas de interface verificadas no navegador.
// Cláusulas: SPEC-030-R01, SPEC-030-R03, SPEC-030-R04, SPEC-030-R05, SPEC-030-R06, SPEC-030-R07,
// SPEC-030-R08, SPEC-030-R09.
// A API real autentica; apenas o perfil (e-mail confirmado) e o mapa de calor são simulados,
// para exibir o componente com dados controlados sem depender de entrega de e-mail.
const position = (items: object[]) => ({ as_of: '2026-11-01', total_absolute: '0', items });
const asset = (id: string, name: string, value: string, rate: string | null) =>
  ({ id, kind: 'asset', name, value, annual_rate: rate, origin: 'manual' });
const liability = (id: string, name: string, value: string, rate: string | null) =>
  ({ id, kind: 'liability', name, value, annual_rate: rate, origin: 'manual' });

async function openHeatmap(page: Page, items: { current: object[] }) {
  const email = `heatmap-${randomUUID()}@example.com`;
  // Perfil com e-mail confirmado montado no teste (sem desligar a verificação TLS do certificado fixado).
  await page.route('**/api/v1/auth/profile', route => route.request().method() !== 'GET' ? route.continue() : route.fulfill({ json: {
    user: { id: randomUUID(), name: 'Helena Mapa', email, role: 'usuario', email_verified: true, investor_profile: null },
    pending_email: null,
    preferences: { language: 'pt', theme: 'light', in_app_notifications: true, email_notifications: false, push_notifications: false },
  } }));
  await page.route('**/api/v1/auth/financial/net-worth/heatmap', route => route.fulfill({ json: position(items.current) }));
  await page.goto('/');
  await page.getByRole('button', { name: 'Criar conta', exact: true }).click();
  await page.getByLabel('Nome', { exact: true }).fill('Helena Mapa');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaSegura123');
  await page.getByRole('button', { name: 'Criar minha conta' }).click();
  await expect(page.getByRole('status')).toContainText('Conta criada');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaSegura123');
  await page.getByRole('button', { name: 'Entrar na conta' }).click();
  await page.getByRole('navigation', { name: 'Seções do FinNova' }).getByRole('button', { name: 'Patrimônio', exact: true }).click();
  return page.getByLabel('Mapa de calor do patrimônio real');
}

test('SPEC-030-R01 a R09: itens, tamanho, cores, detalhes, filtro e atualização', async ({ page }) => {
  const items = { current: [
    asset('a1', 'Imóvel', '300', '6'),
    asset('a2', 'Poupança', '100', '0'),
    liability('l1', 'Cartão', '50', '18'),
    liability('l2', 'Consignado', '50', '2'),
  ] };
  const chart = await openHeatmap(page, items);
  const tiles = chart.getByRole('button');
  // R01/R03: um item por ativo e por passivo.
  await expect(tiles).toHaveCount(4);
  // R04: tamanho proporcional ao valor absoluto (flex-grow = valor).
  await expect(tiles.nth(0)).toHaveCSS('flex-grow', '300');
  await expect(tiles.nth(2)).toHaveCSS('flex-grow', '50');
  await expect(chart.getByRole('button', { name: /^Imóvel: .*, 60\.0%, Ativo$/ })).toBeVisible();
  const color = async (name: string) => chart.getByRole('button', { name: new RegExp(`^${name}:`) })
    .evaluate(element => getComputedStyle(element).backgroundColor);
  const rgb = (value: string) => value.match(/\d+/g)!.map(Number);
  // R06: ativos em verde; rentabilidade nula/negativa em verde claro acinzentado.
  const [r1, g1, b1] = rgb(await color('Imóvel'));
  expect(g1).toBeGreaterThan(r1); expect(g1).toBeGreaterThan(b1);
  expect(await color('Poupança')).toBe('rgb(213, 232, 219)');
  // R05: passivos em tons quentes; juros maiores, vermelho mais intenso.
  const [cr, cg] = rgb(await color('Cartão'));
  const [kr, kg] = rgb(await color('Consignado'));
  expect(cr).toBeGreaterThan(cg); expect(kr).toBeGreaterThan(kg - 1);
  expect(cg).toBeLessThan(kg);
  // R07: detalhes ao passar o mouse/tocar: nome, valor, tipo e indicador da cor.
  await expect(chart.getByRole('button', { name: /^Cartão:/ })).toHaveAttribute('title', /Cartão · Passivo · R\$\s?50,00 · Taxa anual de juros: 18/);
  await chart.getByRole('button', { name: /^Imóvel:/ }).click();
  await expect(page.getByRole('status').filter({ hasText: 'Imóvel' })).toContainText('Rentabilidade anual informada: 6%');
  // R08: filtros todos / somente ativos / somente passivos.
  await page.getByRole('radio', { name: 'Somente passivos' }).check();
  await expect(tiles).toHaveCount(2);
  await page.getByRole('radio', { name: 'Somente ativos' }).check();
  await expect(chart.getByRole('button', { name: /Passivo$/ })).toHaveCount(0);
  await page.getByRole('radio', { name: 'Todos' }).check();
  await expect(tiles).toHaveCount(4);
  // R09: atualiza quando os dados financeiros mudam.
  items.current = [...items.current, asset('a3', 'Reserva', '100', '10')];
  await page.evaluate(() => window.dispatchEvent(new Event('finnova-financial-changed')));
  await expect(tiles).toHaveCount(5);
});
