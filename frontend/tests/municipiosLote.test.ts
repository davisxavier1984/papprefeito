import { test } from 'node:test';
import assert from 'node:assert/strict';
import { guardarLoteAtivo, lerLoteAtivo, statusMaisRecente } from '../src/utils/municipiosLote.ts';
import type { LoteStatus } from '../src/types/index.ts';

const lote = (mudanca: Partial<LoteStatus>): LoteStatus => ({
  id: 'l1',
  status: 'processando',
  competencia: '202508',
  tipos: ['prefeito'],
  total: 10,
  processados: 0,
  arquivos: 0,
  calculados: 0,
  erros: [],
  criado_em: '2026-09-24T10:00:00',
  ...mudanca,
});

test('aceita o primeiro status', () => {
  const novo = lote({ processados: 2 });
  assert.equal(statusMaisRecente(null, novo), novo);
});

test('ignora resposta com menos processados', () => {
  const atual = lote({ processados: 5 });
  assert.equal(statusMaisRecente(atual, lote({ processados: 3 })), atual);
});

test('não volta de concluído para processando', () => {
  const atual = lote({ status: 'concluido', processados: 10 });
  assert.equal(statusMaisRecente(atual, lote({ processados: 9 })), atual);
});

test('aceita avanço e conclusão', () => {
  const concluido = lote({ status: 'concluido', processados: 10 });
  assert.equal(statusMaisRecente(lote({ processados: 9 }), concluido), concluido);
});

test('outro lote substitui o atual', () => {
  const novo = lote({ id: 'l2' });
  assert.equal(statusMaisRecente(lote({ status: 'concluido' }), novo), novo);
});

const memoria = () => {
  const m = new Map<string, string>();
  return {
    getItem: (k: string) => m.get(k) ?? null,
    setItem: (k: string, v: string) => void m.set(k, v),
    removeItem: (k: string) => void m.delete(k),
  };
};

test('guarda, lê e limpa o lote ativo', () => {
  const a = memoria();
  guardarLoteAtivo('l1', a);
  assert.equal(lerLoteAtivo(a), 'l1');
  guardarLoteAtivo(null, a);
  assert.equal(lerLoteAtivo(a), null);
});

test('armazenamento indisponível não quebra', () => {
  const quebrado = {
    getItem: () => {
      throw new Error('bloqueado');
    },
    setItem: () => {
      throw new Error('bloqueado');
    },
    removeItem: () => {
      throw new Error('bloqueado');
    },
  };
  assert.doesNotThrow(() => guardarLoteAtivo('l1', quebrado));
  assert.equal(lerLoteAtivo(quebrado), null);
  assert.equal(lerLoteAtivo(null), null);
});
