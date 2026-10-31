import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { randomUUID } from 'node:crypto';
import { resolve } from 'node:path';
import { readFile } from 'node:fs/promises';

test('cadastro, login, restauração de sessão e logout', async ({ page }) => {
  const email = `e2e-${randomUUID()}@example.com`;
  await page.goto('/');
  await page.getByRole('button', { name: 'Criar conta', exact: true }).click();
  await page.getByLabel('Nome', { exact: true }).fill('Mariana Teste');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaSegura123');
  await page.getByRole('button', { name: 'Criar minha conta' }).click();
  await expect(page.getByRole('status')).toContainText('Conta criada');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaSegura123');
  await page.getByRole('button', { name: 'Entrar na conta' }).click();
  await expect(page.getByRole('heading', { level: 2 })).toContainText('Mariana Teste');
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations).toEqual([]);
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual(['finnova-language']);
  await page.reload();
  await expect(page.getByRole('heading', { level: 2 })).toContainText('Mariana Teste');
  const anotherTab = await page.context().newPage();
  await Promise.all([anotherTab.goto('/'), page.reload()]);
  await expect(anotherTab.getByRole('heading', { level: 2 })).toContainText('Mariana Teste');
  await expect(page.getByRole('heading', { level: 2 })).toContainText('Mariana Teste');
  await anotherTab.close();
  await page.getByRole('button', { name: 'Sair da conta' }).click();
  await expect(page.getByRole('heading', { level: 2 })).toHaveText('Acesse sua conta');
  await page.reload();
  await expect(page.getByRole('heading', { level: 2 })).toHaveText('Acesse sua conta');
});

test('erro genérico e tradução dos formulários e erros', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Idioma').selectOption('en');
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await page.getByLabel('Email', { exact: true }).fill('absent@example.com');
  await page.getByLabel('Password', { exact: true }).fill('WrongPassword123');
  await page.getByRole('button', { name: 'Sign in to your account' }).click();
  await expect(page.getByRole('alert')).toHaveText('Incorrect email or password.');
  await expect(page.getByLabel('Password', { exact: true })).toHaveValue('');
  await page.getByLabel('Language').selectOption('pt');
  await expect(page.getByRole('alert')).toHaveText('E-mail ou senha incorretos.');
});

test('formulários sem violações automáticas WCAG AA e navegação por teclado', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { level: 2 })).toHaveText('Acesse sua conta');
  const scan = () => new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
  expect((await scan()).violations).toEqual([]);
  await page.getByRole('button', { name: 'Criar conta', exact: true }).focus();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { level: 2 })).toHaveText('Vamos começar');
  await page.keyboard.press('Tab');
  await expect(page.getByLabel('Nome', { exact: true })).toBeFocused();
  expect((await scan()).violations).toEqual([]);
});

test('layout mobile e desktop sem rolagem horizontal', async ({ page }) => {
  for (const width of [320, 390, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.goto('/');
    await expect(page.getByRole('heading', { level: 2 })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page.getByRole('button', { name: 'Entrar na conta' })).toBeVisible();
  }
});

test('Swagger carrega os contratos sem depender de CDN', async ({ page }) => {
  const external: string[] = [];
  page.on('request', request => {
    if (!request.url().startsWith('https://localhost:8443/')) external.push(request.url());
  });
  await page.goto('/api/v1/docs');
  await expect(page.locator('.swagger-ui .opblock-summary-path[data-path="/api/v1/auth/login"]')).toBeVisible();
  expect(external).toEqual([]);
});

test('prévia HTML abre sozinha sem rede, servidor ou armazenamento local', async ({ page }) => {
  const network: string[] = [];
  const errors: string[] = [];
  page.on('request', request => {
    if (/^https?:/.test(request.url())) network.push(request.url());
  });
  page.on('pageerror', error => errors.push(error.message));
  await page.route(/^https?:/, route => route.abort());
  await page.evaluate(() => Object.defineProperty(window, 'localStorage', {
    get() { throw new DOMException('Storage blocked', 'SecurityError'); },
  }));
  // The managed Chromium blocks file: navigation. Load the exact standalone
  // HTML into a blank document and block all HTTP requests instead.
  await page.setContent(await readFile(resolve('../.local/finnova-preview.html'), 'utf8'));
  await expect(page.getByRole('heading', { level: 2 })).toHaveText('Acesse sua conta');
  await expect(page.getByRole('note')).toContainText('Prévia visual');
  await expect(page.getByRole('button', { name: 'Entrar na conta' })).toBeDisabled();
  await page.getByRole('button', { name: 'Criar conta', exact: true }).click();
  await expect(page.getByLabel('Nome', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Criar minha conta' })).toBeDisabled();
  await page.getByLabel('Idioma').selectOption('en');
  await expect(page.getByRole('note')).toContainText('Visual preview');
  expect(network).toEqual([]);
  expect(errors).toEqual([]);
});

test('SPEC-001-R11: quinta falha informa bloqueio com prazo e mantém tradução', async ({ page }) => {
  const email = `lock-${randomUUID()}@example.com`;
  await page.goto('/');
  await page.getByRole('button', { name: 'Criar conta', exact: true }).click();
  await page.getByLabel('Nome', { exact: true }).fill('Art Teste');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaForte123');
  await page.getByRole('button', { name: 'Criar minha conta' }).click();
  await expect(page.getByRole('status')).toContainText('Conta criada');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  for (let i = 0; i < 5; i++) {
    await page.getByLabel('Senha', { exact: true }).fill('WrongPassword123');
    await page.getByRole('button', { name: 'Entrar na conta' }).click();
    await expect(page.getByLabel('Senha', { exact: true })).toHaveValue('');
    await expect(page.getByRole('alert')).toContainText(i < 4 ? 'E-mail ou senha incorretos' : 'Acesso temporariamente indisponível');
  }
  await expect(page.locator('.retry-countdown')).toContainText(/14:5\d|15:00/);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaForte123');
  await page.getByRole('button', { name: 'Entrar na conta' }).click();
  await expect(page.getByRole('alert')).toContainText('Acesso temporariamente indisponível');
  await page.getByLabel('Idioma').selectOption('en');
  await expect(page.getByRole('alert')).toContainText('Sign-in temporarily unavailable');
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations).toEqual([]);
});

test('demonstração interativa sem API: cadastro, bloqueio, avanço de tempo e logout', async ({ page }) => {
  const network: string[] = [];
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => { if (/^https?:/.test(request.url())) network.push(request.url()); });
  await page.route(/^https?:/, route => route.abort());
  await page.setContent(await readFile(resolve('../.local/finnova-demo.html'), 'utf8'));
  await expect(page.getByRole('heading', { level: 2 })).toHaveText('Acesse sua conta');
  await page.setViewportSize({ width: 1024, height: 900 });
  await page.screenshot({ path: '../.local/demo-login.png', fullPage: true });
  await page.getByLabel('E-mail', { exact: true }).fill('art@exemplo.com');
  for (let i = 0; i < 5; i++) {
    await page.getByLabel('Senha', { exact: true }).fill('WrongPassword123');
    await page.getByRole('button', { name: 'Entrar na conta' }).click();
    await expect(page.getByRole('alert')).toContainText(i < 4 ? 'E-mail ou senha incorretos' : 'Acesso temporariamente indisponível');
  }
  await page.screenshot({ path: '../.local/demo-bloqueio.png', fullPage: true });
  await page.getByRole('button', { name: 'Avançar 15 minutos' }).click();
  await page.getByLabel('Senha', { exact: true }).fill('SenhaForte123');
  await page.getByRole('button', { name: 'Entrar na conta' }).click();
  await expect(page.getByRole('heading', { level: 2 })).toContainText('Art');
  await page.getByRole('button', { name: 'Sair da conta' }).click();
  await expect(page.getByRole('heading', { level: 2 })).toHaveText('Acesse sua conta');
  await page.getByRole('button', { name: 'Criar conta', exact: true }).click();
  await page.getByLabel('Nome', { exact: true }).fill('Mariana Demo');
  await page.getByLabel('E-mail', { exact: true }).fill('mariana@exemplo.com');
  await page.getByLabel('Senha', { exact: true }).fill('SenhaDemo123');
  await page.getByRole('button', { name: 'Criar minha conta' }).click();
  await expect(page.getByRole('status')).toContainText('Conta criada');
  await page.getByLabel('E-mail', { exact: true }).fill('mariana@exemplo.com');
  await page.getByLabel('Senha', { exact: true }).fill('SenhaDemo123');
  await page.getByRole('button', { name: 'Entrar na conta' }).click();
  await expect(page.getByRole('heading', { level: 2 })).toContainText('Mariana Demo');
  await page.getByRole('button', { name: 'Sair da conta' }).click();
  for (const width of [320, 1024]) {
    await page.setViewportSize({ width, height: 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
  expect(errors).toEqual([]);
  expect(network).toEqual([]);
});
