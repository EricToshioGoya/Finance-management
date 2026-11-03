import { test } from 'node:test';
import assert from 'node:assert/strict';
import { currentCompetence, money, parseAmount, today } from './format.ts';

test('formata moeda em pt-BR', () => {
  assert.equal(money('15000.5'), 'R$ 15.000,50');
  assert.equal(money(-2.1), '-R$ 2,10');
  assert.equal(money(null), 'R$ 0,00');
});

test('competência e data no fuso de São Paulo', () => {
  const lateNightUtc = new Date('2026-11-01T02:00:00Z'); // ainda 31/10 em São Paulo
  assert.equal(currentCompetence(lateNightUtc), '2026-10');
  assert.equal(today(lateNightUtc), '2026-10-31');
});

test('competência e data no fuso de São Paulo na virada do ano', () => {
  const newYearUtc = new Date('2027-01-01T02:59:00Z'); // ainda 31/12/2026 às 23:59 em São Paulo
  assert.equal(today(newYearUtc), '2026-12-31');
  assert.equal(currentCompetence(newYearUtc), '2026-12');
  assert.equal(today(new Date('2027-01-01T03:00:00Z')), '2027-01-01');
});

test('valor digitado em pt-BR vira decimal da API', () => {
  assert.equal(parseAmount('1.234,56'), '1234.56');
  assert.equal(parseAmount('R$ 15,5'), '15.5');
  assert.equal(parseAmount('1234.56'), '1234.56');
  assert.equal(parseAmount('12'), '12');
  assert.equal(parseAmount('1,234,56'), null);
  assert.equal(parseAmount('abc'), null);
  assert.equal(parseAmount('1,999'), null);
});
