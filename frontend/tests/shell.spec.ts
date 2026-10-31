import { expect, test } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { randomUUID } from 'node:crypto';

// Navegação autenticada por abas: acessibilidade, bloqueio por e-mail não confirmado e layout sem rolagem lateral.
test('shell autenticado: abas, verificação de e-mail e acessibilidade', async ({ page }) => {
  const email = `shell-${randomUUID()}@example.com`;
  await page.goto('/');
  await page.getByRole('button', { name: 'Criar conta', exact: true }).click();
  await page.getByLabel('Nome', { exact: true }).fill('Bruna Abas');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaSegura123');
  await page.getByRole('button', { name: 'Criar minha conta' }).click();
  await expect(page.getByRole('status')).toContainText('Conta criada');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaSegura123');
  await page.getByRole('button', { name: 'Entrar na conta' }).click();
  await expect(page.getByRole('heading', { level: 2 })).toContainText('Bruna Abas');
  const nav = page.getByRole('navigation', { name: 'Seções do FinNova' });
  for (const name of ['Visão geral', 'Lançamentos', 'Planejamento', 'Investimentos', 'Patrimônio', 'Minha conta']) {
    await expect(nav.getByRole('button', { name, exact: true })).toBeVisible();
  }
  await expect(nav.getByRole('button', { name: 'Administração' })).toHaveCount(0);
  await nav.getByRole('button', { name: 'Lançamentos', exact: true }).click();
  await expect(nav.getByRole('button', { name: 'Lançamentos', exact: true })).toHaveAttribute('aria-current', 'page');
  await expect(page.getByText('Confirme seu e-mail', { exact: false }).first()).toBeVisible();
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations).toEqual([]);
  await nav.getByRole('button', { name: 'Minha conta', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Excluir conta' })).toBeVisible();
  expect((await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations).toEqual([]);
  for (const width of [320, 390, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
});
