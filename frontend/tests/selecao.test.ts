import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mesmaSelecao } from '../src/utils/selecao.ts';

test('mesma seleção', () => {
  assert.equal(mesmaSelecao({ codigo_ibge: '290020', competencia: '202508' }, { codigo_ibge: '290020', competencia: '202508' }), true);
});

test('município diferente', () => {
  assert.equal(mesmaSelecao({ codigo_ibge: '290020', competencia: '202508' }, { codigo_ibge: '292740', competencia: '202508' }), false);
});

test('competência diferente', () => {
  assert.equal(mesmaSelecao({ codigo_ibge: '290020', competencia: '202508' }, { codigo_ibge: '290020', competencia: '202507' }), false);
});

test('seleção vazia nunca é igual', () => {
  assert.equal(mesmaSelecao({ codigo_ibge: '', competencia: '' }, { codigo_ibge: '', competencia: '' }), false);
});
