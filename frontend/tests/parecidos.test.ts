import { test } from 'node:test';
import assert from 'node:assert/strict';
import { competenciaCurta, resumoParecidos } from '../src/utils/parecidos.ts';

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

test('competência curta', () => {
  assert.equal(competenciaCurta('202606'), '06/2026');
});

test('resumo dos parecidos', () => {
  const texto = resumoParecidos(
    [
      { codigo_ibge: '1', competencia: '202606', municipio: 'MARICA', uf: 'RJ', valor: 27300, distancia: 0.1 },
      { codigo_ibge: '2', competencia: '202512', municipio: 'BARRA', uf: 'BA', valor: 25000, distancia: 0.2 },
    ],
    moeda
  );
  assert.match(texto, /^MARICA\/RJ 06\/2026 R\$\s27\.300,00 · BARRA\/BA 12\/2025 R\$\s25\.000,00$/);
});

test('sem exemplos', () => {
  assert.equal(resumoParecidos([], moeda), '');
});
