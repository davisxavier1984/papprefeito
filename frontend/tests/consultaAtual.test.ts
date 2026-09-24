import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ehConsultaAtual } from '../src/utils/consultaAtual.ts';

test('consulta mais recente é a atual', () => {
  assert.equal(ehConsultaAtual(3, 3), true);
});

test('consulta antiga não é mais a atual', () => {
  assert.equal(ehConsultaAtual(2, 3), false);
});
