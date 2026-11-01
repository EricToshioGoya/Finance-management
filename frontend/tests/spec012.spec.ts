import { expect, test } from '@playwright/test';
import { randomUUID } from 'node:crypto';

// SPEC-012-R04, SPEC-012-R11 e SPEC-012-R12: sugestões ao digitar, link oficial em nova aba e aviso de responsabilidade.
test('SPEC-012: sugere empresas ao digitar e abre documento oficial em nova aba com aviso', async ({ page }) => {
  const email = `empresas-${randomUUID()}@example.com`;
  await page.goto('/');
  await page.getByRole('button', { name: 'Criar conta', exact: true }).click();
  await page.getByLabel('Nome', { exact: true }).fill('Caio Empresas');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaSegura123');
  await page.getByRole('button', { name: 'Criar minha conta' }).click();
  await expect(page.getByRole('status')).toContainText('Conta criada');
  await page.getByLabel('E-mail', { exact: true }).fill(email);
  await page.getByLabel('Senha', { exact: true }).fill('SenhaSegura123');
  await page.getByRole('button', { name: 'Entrar na conta' }).click();
  const nav = page.getByRole('navigation', { name: 'Seções do FinNova' });
  await nav.getByRole('button', { name: 'Empresas', exact: true }).click();

  // R04: sem enviar o formulário, as sugestões aparecem conforme a digitação.
  await page.getByLabel('Ticker, CNPJ ou razão social').pressSequentially('PETR', { delay: 50 });
  const suggestions = page.getByRole('list', { name: 'Sugestões de empresas' });
  await expect(suggestions.getByRole('button', { name: /^PETR4 — / })).toBeVisible();
  await suggestions.getByRole('button', { name: /^PETR4 — / }).click();

  // R12: aviso de responsabilidade da emissora e da CVM.
  await expect(page.getByText('O FinNova apenas indexa e referencia este material.', { exact: false })).toBeVisible();
  // R11: link direto para o RAD/ENET, aberto em nova aba sem acesso ao opener.
  const link = page.getByRole('link', { name: 'Abrir documento oficial' }).first();
  await expect(link).toHaveAttribute('target', '_blank');
  await expect(link).toHaveAttribute('rel', /noopener/);
  await expect(link).toHaveAttribute('href', /^https:\/\/www\.rad\.cvm\.gov\.br\//);
});
