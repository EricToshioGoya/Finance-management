import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ApiError, createApi, newIdempotencyKey } from './http.ts';

type Chamada = { url: string; init: RequestInit };

// Dublê do fetch: registra a chamada e devolve a resposta preparada (C-17).
function duble(resposta: () => Response) {
  const chamadas: Chamada[] = [];
  const api = createApi('https://api.exemplo', async (url, init) => {
    chamadas.push({ url, init });
    return resposta();
  });
  return { api, chamadas };
}

test('usa o prefixo /api/v1 e envia token e JSON só quando há', async () => {
  const { api, chamadas } = duble(() => Response.json({ ok: true }));
  assert.deepEqual(await api('/auth/me', 'tok-1'), { ok: true });
  await api('/auth/login', null, { method: 'POST', body: '{}' });
  assert.equal(chamadas[0].url, 'https://api.exemplo/api/v1/auth/me');
  assert.deepEqual(chamadas[0].init.headers, { Authorization: 'Bearer tok-1' });
  assert.deepEqual(chamadas[1].init.headers, { 'Content-Type': 'application/json' });
});

test('preserva a chave de idempotência enviada pelo chamador', async () => {
  const { api, chamadas } = duble(() => Response.json({}, { status: 201 }));
  await api('/auth/financial/expenses', 'tok', { method: 'POST', body: '{}', headers: { 'Idempotency-Key': 'k-1' } });
  assert.equal((chamadas[0].init.headers as Record<string, string>)['Idempotency-Key'], 'k-1');
});

test('204 devolve undefined sem ler corpo', async () => {
  const { api } = duble(() => new Response(null, { status: 204 }));
  assert.equal(await api('/auth/logout', 'tok', { method: 'POST' }), undefined);
});

test('erro da API expõe só o código; corpo inválido vira erro genérico', async () => {
  await assert.rejects(duble(() => Response.json({ detail: 'invalid_session' }, { status: 401 })).api('/x', 't'),
    (erro: unknown) => erro instanceof ApiError && erro.message === 'invalid_session');
  await assert.rejects(duble(() => new Response('<html>', { status: 502 })).api('/x', 't'),
    (erro: unknown) => erro instanceof ApiError && erro.message === 'service_unavailable');
  await assert.rejects(duble(() => Response.json({ detail: [{ msg: 'x' }] }, { status: 422 })).api('/x', 't'),
    (erro: unknown) => erro instanceof ApiError && erro.message === 'service_unavailable');
});

test('chaves de idempotência novas são distintas e cabem no limite da API', () => {
  const chaves = new Set(Array.from({ length: 1000 }, newIdempotencyKey));
  assert.equal(chaves.size, 1000);
  for (const chave of chaves) assert.ok(chave.length >= 1 && chave.length <= 128);
});
