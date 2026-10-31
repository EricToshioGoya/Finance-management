import { test } from 'node:test';
import assert from 'node:assert/strict';
import { currentCompetence, money, today } from './format.ts';

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
